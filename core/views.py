# core/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count

from .models import TeamMember, Holiday, DutyType, DutySchedule
from .forms import HolidayForm, DutyScheduleForm

# core/views.py - Atualize a função home_view

def home_view(request):
    """Página inicial com visão geral das atividades do dia e próximos dias úteis"""
    today = timezone.now().date()
    
    # Busca as tarefas de hoje
    today_duties = DutySchedule.objects.filter(date=today).select_related('member', 'duty_type')
    
    # Busca os feriados cadastrados
    holidays = Holiday.objects.filter(
        date__gte=today
    ).values_list('date', flat=True)
    
    # Encontra os próximos 7 dias úteis (excluindo finais de semana e feriados)
    upcoming_dates = []
    current_date = today
    while len(upcoming_dates) < 7:  # Queremos exatamente 7 dias úteis
        # Verifica se não é final de semana (0=segunda, 6=domingo)
        if current_date.weekday() < 5 and current_date not in holidays:
            upcoming_dates.append(current_date)
        current_date += timedelta(days=1)
    
    # Busca as tarefas para os próximos 7 dias úteis
    upcoming_duties = DutySchedule.objects.filter(
        date__in=upcoming_dates
    ).select_related('member', 'duty_type').order_by('date', 'duty_type__time')
    
    # Estatísticas
    stats = {
        'total_coffees': DutySchedule.objects.filter(
            duty_type__name__icontains='Reabastecimento', 
            completed=True
        ).count(),
        'total_cleanings': DutySchedule.objects.filter(
            duty_type__name__icontains='Limpeza', 
            completed=True
        ).count(),
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
    
    return render(request, 'core/schedule.html', {
        'duties': duties,
        'holidays': holidays,
        'start_date': today,
        'end_date': end_date
    })

@login_required
def holiday_list(request):
    """Lista de feriados cadastrados"""
    today = timezone.now().date()
    holidays = Holiday.objects.filter(date__gte=today).order_by('date')
    past_holidays = Holiday.objects.filter(date__lt=today).order_by('-date')
    
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
    """Marcar uma tarefa como concluída"""
    duty = get_object_or_404(DutySchedule, pk=duty_id)
    
    # Alterna o estado da tarefa
    duty.completed = not duty.completed
    duty.save()
    
    messages.success(request, f'Tarefa marcada como {"concluída" if duty.completed else "pendente"}.')
    return redirect('home')



@login_required
def team_member_list(request):
    """Lista de membros da equipe"""
    members = TeamMember.objects.all().order_by('name')
    
    return render(request, 'core/team_member_list.html', {
        'members': members
    })

@login_required
def team_member_create(request):
    """Cadastro de novo membro da equipe"""
    if request.method == 'POST':
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membro cadastrado com sucesso.')
            return redirect('team_member_list')
    else:
        form = TeamMemberForm()
    
    return render(request, 'core/team_member_form.html', {
        'form': form,
        'title': 'Novo Membro'
    })

@login_required
def team_member_edit(request, pk):
    """Edição de membro existente"""
    member = get_object_or_404(TeamMember, pk=pk)
    
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membro atualizado com sucesso.')
            return redirect('team_member_list')
    else:
        form = TeamMemberForm(instance=member)
    
    return render(request, 'core/team_member_form.html', {
        'form': form,
        'member': member,
        'title': 'Editar Membro'
    })

@login_required
def team_member_toggle_active(request, pk):
    """Ativar/desativar um membro da equipe"""
    member = get_object_or_404(TeamMember, pk=pk)
    member.is_active = not member.is_active
    member.save()
    
    status = "ativado" if member.is_active else "desativado"
    messages.success(request, f'Membro {member.name} {status} com sucesso.')
    return redirect('team_member_list')

@login_required
def generate_schedule(request):
    """View para gerar escala manualmente"""
    if request.method == 'POST':
        days = int(request.POST.get('days', 30))
        
        generator = ScheduleGenerator(days_to_generate=days)
        created = generator.generate_schedule()
        
        if created:
            messages.success(request, f'Sucesso! {created} escalas foram geradas.')
        else:
            messages.warning(request, 'Nenhuma escala foi gerada. Verifique se existem membros ativos e tipos de tarefa configurados.')
        
        return redirect('schedule')
    
    return render(request, 'core/generate_schedule.html', {
        'title': 'Gerar Escala'
    })