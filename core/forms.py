# core/forms.py

from django import forms
from .models import Holiday, DutySchedule, TeamMember

class HolidayForm(forms.ModelForm):
    """Formulário para cadastro/edição de feriados"""
    class Meta:
        model = Holiday
        fields = ['date', 'name']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class DutyScheduleForm(forms.ModelForm):
    """Formulário para cadastro/edição de escalas"""
    class Meta:
        model = DutySchedule
        fields = ['member', 'duty_type', 'date', 'completed']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-select'}),
            'duty_type': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'completed': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        
        
class TeamMemberForm(forms.ModelForm):
    """Formulário para cadastro/edição de membros da equipe"""
    class Meta:
        model = TeamMember
        fields = ['name', 'email', 'phone', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }