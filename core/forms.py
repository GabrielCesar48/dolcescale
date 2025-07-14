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
        fields = ['avatar', 'phone', 'exit_time', 'cleaning_preference']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: (35) 99999-9999'
            }),
            'exit_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '300'  # Intervalos de 5 minutos
            }),
            'cleaning_preference': forms.Select(attrs={'class': 'form-select'})
        }
        help_texts = {
            'exit_time': 'Seu horário habitual de saída da empresa',
            'cleaning_preference': 'Como calcular seu horário ideal de limpeza'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona classes CSS e validações
        self.fields['exit_time'].widget.attrs.update({
            'min': '16:00',
            'max': '19:00'
        })
        
        # Personaliza labels
        self.fields['exit_time'].label = 'Horário de Saída'
        self.fields['cleaning_preference'].label = 'Preferência de Limpeza'
        self.fields['phone'].label = 'Telefone/WhatsApp'
        self.fields['avatar'].label = 'Foto do Perfil'
    
    def clean_exit_time(self):
        """Valida o horário de saída"""
        exit_time = self.cleaned_data.get('exit_time')
        
        if exit_time:
            # Converte para minutos para facilitar comparação
            exit_minutes = exit_time.hour * 60 + exit_time.minute
            
            # Horário mínimo: 16:00 (960 minutos)
            # Horário máximo: 19:00 (1140 minutos)
            if exit_minutes < 960:
                raise forms.ValidationError('Horário de saída não pode ser antes das 16:00')
            
            if exit_minutes > 1140:
                raise forms.ValidationError('Horário de saída não pode ser depois das 19:00')
        
        return exit_time

class CustomPasswordChangeForm(PasswordChangeForm):
    """Form personalizado para alterar senha"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class TeamMemberPreferencesForm(forms.ModelForm):
    """Formulário específico para preferências de limpeza"""
    class Meta:
        model = TeamMember
        fields = ['exit_time', 'cleaning_preference']
        widgets = {
            'exit_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'step': '300'
            }),
            'cleaning_preference': forms.RadioSelect(attrs={'class': 'form-check-input'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personaliza o widget de preferências para usar radio buttons
        self.fields['cleaning_preference'].widget = forms.RadioSelect(
            choices=TeamMember.CLEANING_PREFERENCES
        )
        
        # Adiciona informações úteis nos labels
        self.fields['exit_time'].label = 'Seu horário de saída'
        self.fields['cleaning_preference'].label = 'Como calcular seu horário de limpeza'
        
        # Adiciona help text dinâmico
        if self.instance and self.instance.pk:
            cleaning_time = self.instance.get_cleaning_time_display()
            self.fields['exit_time'].help_text = f'Horário atual de limpeza: {cleaning_time}'
    
    def clean(self):
        """Validação customizada do formulário"""
        cleaned_data = super().clean()
        exit_time = cleaned_data.get('exit_time')
        preference = cleaned_data.get('cleaning_preference')
        
        if exit_time and preference == 'auto':
            # Calcula o horário de limpeza baseado na saída
            from datetime import datetime, timedelta
            exit_datetime = datetime.combine(datetime.today(), exit_time)
            cleaning_datetime = exit_datetime - timedelta(minutes=30)
            cleaning_time = cleaning_datetime.time()
            
            # Verifica se o horário de limpeza é razoável (entre 16:00 e 18:00)
            if cleaning_time.hour < 16:
                self.add_error('exit_time', 'Com esse horário de saída, a limpeza seria muito cedo (antes das 16:00)')
            elif cleaning_time.hour >= 18:
                self.add_error('exit_time', 'Com esse horário de saída, a limpeza seria muito tarde (depois das 18:00)')
        
        return cleaned_data