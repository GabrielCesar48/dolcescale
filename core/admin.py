# core/admin.py

from django.contrib import admin
from .models import TeamMember, Holiday, DutyType, DutySchedule

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'email')

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
    search_fields = ('member__user__username', 'member__user__first_name')
    date_hierarchy = 'date'
    list_editable = ('completed',)