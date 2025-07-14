# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.utils import timezone
from datetime import timedelta, date
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db import models

from .models import TeamMember, Holiday, DutyType, DutySchedule
from .forms import HolidayForm, DutyScheduleForm, ProfileForm, CustomPasswordChangeForm

def home_view(request):
    """Página inicial com visão geral das atividades do dia"""
    today = timezone.now().date()
    
    # Busca a limpeza de hoje (apenas uma por dia agora)
    today_duties = DutySchedule.objects.filter(date=today).select_related('member', 'duty_type')
    
    # Busca as próximas 7 dias de limpezas
    end_date = today + timedelta(days=6)  # 7 dias incluindo hoje
    upcoming_duties = DutySchedule.objects.filter(
        date__gte=today,
        date__lte=end_date
    ).select_related('member', 'duty_type').order_by('date', 'duty_type__time')
    
    # Estatísticas atualizadas
    total_coffees = DutySchedule.objects.filter(
        completed=True
    ).aggregate(models.Sum('coffees_served'))['coffees_served__sum'] or 0
    
    # Como agora é só limpeza, contamos todas as limpezas concluídas
    total_cleanings = DutySchedule.objects.filter(completed=True).count()
    
    stats = {
        'total_coffees': total_coffees,
        'total_cleanings': total_cleanings,
        'team_members': TeamMember.objects.filter(is_active=True).count(),
        'holidays': Holiday.objects.filter(date__gte=today).count(),
    }
    
    return render(request, 'core/home.html', {
        'today_duties': today_duties,
        'upcoming_duties': upcoming_duties,
        'stats': stats,
        'today_date': today,
    })

def schedule_view(request):
    """Exibe o cronograma completo"""
    today = timezone.now().date()
    end_date = today + timedelta(days=30)  # próximos 30 dias
    
    duties = DutySchedule.objects.filter(
        date__gte=today,
        date__lte=end_date
    ).select_related('member', 'duty_type').order_by('date', 'duty_type__time')
    
    holidays = Holiday.objects.filter(
        date__gte=today,
        date__lte=end_date
    ).order_by('date')
    
    # Estatísticas do período
    schedule_stats = {
        'total_duties': duties.count(),
        'completed_duties': duties.filter(completed=True).count(),
        'time_16_30_count': duties.filter(duty_type__time__hour=16).count(),
        'time_17_30_count': duties.filter(duty_type__time__hour=17).count(),
    }
    
    return render(request, 'core/schedule.html', {
        'duties': duties,
        'holidays': holidays,
        'start_date': today,
        'end_date': end_date,
        'schedule_stats': schedule_stats
    })

@login_required
def holiday_list(request):
    """Lista de feriados cadastrados"""
    today = timezone.now().date()
    holidays = Holiday.objects.filter(date__gte=today).order_by('date')
    past_holidays = Holiday.objects.filter(date__lt=today).order_by('-date')[:10]  # Últimos 10
    
    return render(request, 'core/holiday_list.html', {
        'holidays': holidays,
        'past_holidays': past_holidays
    })

@login_required
def holiday_create(request):
    """Cadastro de novo feriado"""
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feriado cadastrado com sucesso.')
            return redirect('holiday_list')
    else:
        form = HolidayForm()
    
    return render(request, 'core/holiday_form.html', {
        'form': form,
        'title': 'Novo Feriado'
    })

@login_required
def holiday_edit(request, pk):
    """Edição de feriado existente"""
    holiday = get_object_or_404(Holiday, pk=pk)
    
    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feriado atualizado com sucesso.')
            return redirect('holiday_list')
    else:
        form = HolidayForm(instance=holiday)
    
    return render(request, 'core/holiday_form.html', {
        'form': form,
        'holiday': holiday,
        'title': 'Editar Feriado'
    })

@login_required
def mark_completed(request, duty_id):
    """Marcar uma limpeza como concluída"""
    duty = get_object_or_404(DutySchedule, pk=duty_id)
    
    # Alterna o estado da limpeza
    duty.completed = not duty.completed
    duty.save()
    
    action = "concluída" if duty.completed else "pendente"
    messages.success(request, f'Limpeza de {duty.date.strftime("%d/%m")} às {duty.duty_type.time.strftime("%H:%M")} marcada como {action}.')
    
    # Redireciona para a página anterior ou home
    next_page = request.GET.get('next', 'home')
    return redirect(next_page)

def login_view(request):
    """View para login de usuário"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'home')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bem-vindo, {user.get_full_name() or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Nome de usuário ou senha incorretos.')
    
    return render(request, 'core/login.html')

@login_required
def profile_view(request):
    """View para edição de perfil do usuário"""
    try:
        team_member = TeamMember.objects.get(user=request.user)
    except TeamMember.DoesNotExist:
        messages.error(request, "Perfil de membro não encontrado para este usuário.")
        return redirect('home')
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            profile_form = ProfileForm(request.POST, request.FILES, instance=team_member)
            password_form = CustomPasswordChangeForm(request.user)
            
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Seu perfil foi atualizado com sucesso!')
                return redirect('profile')
        
        elif form_type == 'password':
            profile_form = ProfileForm(instance=team_member)
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Sua senha foi atualizada com sucesso!')
                return redirect('profile')
    else:
        profile_form = ProfileForm(instance=team_member)
        password_form = CustomPasswordChangeForm(request.user)
    
    # Estatísticas do usuário
    user_stats = {
        'total_duties': DutySchedule.objects.filter(member=team_member).count(),
        'completed_duties': DutySchedule.objects.filter(member=team_member, completed=True).count(),
        'next_duty': DutySchedule.objects.filter(
            member=team_member, 
            date__gte=timezone.now().date(),
            completed=False
        ).order_by('date').first()
    }
    
    return render(request, 'core/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'user_stats': user_stats,
    })

@login_required
def schedule_stats_api(request):
    """API para estatísticas do cronograma (para gráficos futuros)"""
    today = timezone.now().date()
    
    # Estatísticas dos últimos 30 dias
    start_date = today - timedelta(days=30)
    
    stats = {
        'period': {
            'start': start_date.isoformat(),
            'end': today.isoformat()
        },
        'distribution_by_time': {
            '16:30': DutySchedule.objects.filter(
                date__gte=start_date,
                duty_type__time__hour=16
            ).count(),
            '17:30': DutySchedule.objects.filter(
                date__gte=start_date,
                duty_type__time__hour=17
            ).count()
        },
        'completion_rate': {
            'completed': DutySchedule.objects.filter(
                date__gte=start_date,
                completed=True
            ).count(),
            'total': DutySchedule.objects.filter(date__gte=start_date).count()
        },
        'members_activity': {}
    }
    
    # Atividade por membro
    for member in TeamMember.objects.filter(is_active=True):
        member_duties = DutySchedule.objects.filter(
            member=member,
            date__gte=start_date
        )
        stats['members_activity'][str(member)] = {
            'total': member_duties.count(),
            'completed': member_duties.filter(completed=True).count()
        }
    
    return JsonResponse(stats)