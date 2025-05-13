# core/admin.py

from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import TeamMember, Holiday, DutyType, DutySchedule
from .services.schedule_generator import ScheduleGenerator

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'email')
    list_editable = ('is_active',)

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_filter = ('date',)
    search_fields = ('name',)
    date_hierarchy = 'date'

@admin.register(DutyType)
class DutyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'time', 'description')

@admin.register(DutySchedule)
class DutyScheduleAdmin(admin.ModelAdmin):
    list_display = ('member', 'duty_type', 'date', 'completed', 'notification_sent')
    list_filter = ('completed', 'notification_sent', 'duty_type', 'date')
    search_fields = ('member__name',)
    date_hierarchy = 'date'
    list_editable = ('completed',)
    actions = ['mark_as_completed', 'generate_schedule_action']
    
    def mark_as_completed(self, request, queryset):
        """Marca as tarefas selecionadas como concluídas"""
        updated = queryset.update(completed=True)
        self.message_user(
            request,
            f"{updated} {'tarefa foi marcada' if updated == 1 else 'tarefas foram marcadas'} como concluída(s).",
            messages.SUCCESS
        )
    mark_as_completed.short_description = "Marcar tarefas selecionadas como concluídas"
    
    def generate_schedule_action(self, request, queryset):
        """Gera escala para os próximos 30 dias"""
        generator = ScheduleGenerator(days_to_generate=30)
        created = generator.generate_schedule()
        
        if created:
            self.message_user(
                request,
                f"Sucesso! {created} novas escalas foram geradas.",
                messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                "Nenhuma escala foi gerada. Verifique se existem membros ativos e tipos de tarefa configurados.",
                messages.WARNING
            )
    generate_schedule_action.short_description = "Gerar escala para próximos 30 dias"