# core/forms.py

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
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

class ProfileForm(forms.ModelForm):
    """Formulário para edição de perfil de usuário"""
    class Meta:
        model = TeamMember
        fields = ['avatar', 'phone']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'})
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """Form personalizado para alterar senha"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})