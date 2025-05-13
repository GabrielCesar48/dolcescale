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

def home_view(request):
    """Página inicial com visão geral das atividades do dia"""
    today = timezone.now().date()
    
    # Busca as tarefas de hoje
    today_duties = DutySchedule.objects.filter(date=today).select_related('member', 'duty_type')
    
    # Busca as próximas 7 dias de tarefas
    end_date = today + timedelta(days=6)  # 7 dias incluindo hoje
    upcoming_duties = DutySchedule.objects.filter(
        date__gte=today,
        date__lte=end_date
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