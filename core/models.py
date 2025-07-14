from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time, datetime, timedelta

class TeamMember(models.Model):
    """Modelo para membros da equipe de TI"""
    CLEANING_PREFERENCES = [
        ('auto', 'Automático (30min antes da saída)'),
        ('early', 'Preferência por horário mais cedo'),
        ('late', 'Preferência por horário mais tarde')
    ]
    
    email = models.EmailField(unique=True, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, help_text="Número de WhatsApp", null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    exit_time = models.TimeField(
        default=time(18, 0),
        help_text="Horário de saída da empresa (usado para calcular horário de limpeza)"
    )
    cleaning_preference = models.CharField(
        max_length=20,
        choices=CLEANING_PREFERENCES,
        default='auto',
        help_text="Como calcular o horário de limpeza"
    )
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    def get_cleaning_time(self):
        """Calcula o horário ideal de limpeza baseado no horário de saída"""
        if self.cleaning_preference == 'auto':
            # Subtrai 30 minutos do horário de saída
            exit_datetime = datetime.combine(datetime.today(), self.exit_time)
            cleaning_datetime = exit_datetime - timedelta(minutes=30)
            return cleaning_datetime.time()
        
        elif self.cleaning_preference == 'early':
            # Sempre escolhe o horário mais cedo disponível (16:30)
            return time(16, 30)
        
        elif self.cleaning_preference == 'late':
            # Sempre escolhe o horário mais tarde disponível (17:30)
            return time(17, 30)
        
        # Fallback para automático
        exit_datetime = datetime.combine(datetime.today(), self.exit_time)
        cleaning_datetime = exit_datetime - timedelta(minutes=30)
        return cleaning_datetime.time()
    
    def get_cleaning_time_display(self):
        """Retorna o horário de limpeza formatado para exibição"""
        cleaning_time = self.get_cleaning_time()
        return cleaning_time.strftime('%H:%M')
    
    def get_exit_time_display(self):
        """Retorna o horário de saída formatado"""
        return self.exit_time.strftime('%H:%M')
    
    @property
    def cleaning_window_minutes(self):
        """Retorna quantos minutos de antecedência para limpeza"""
        exit_datetime = datetime.combine(datetime.today(), self.exit_time)
        cleaning_datetime = datetime.combine(datetime.today(), self.get_cleaning_time())
        delta = exit_datetime - cleaning_datetime
        return int(delta.total_seconds() / 60)

class Holiday(models.Model):
    """Modelo para feriados"""
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.date})"

class DutyType(models.Model):
    """Tipo de tarefa (limpeza diária)"""
    name = models.CharField(max_length=50)
    time = models.TimeField()  # Horário da tarefa
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name} ({self.time})"
    
    @classmethod
    def get_best_duty_type_for_member(cls, member):
        """Retorna o tipo de tarefa mais adequado para o membro"""
        ideal_time = member.get_cleaning_time()
        
        # Busca o tipo de tarefa mais próximo do horário ideal
        duty_types = cls.objects.all()
        best_match = None
        min_difference = None
        
        for duty_type in duty_types:
            # Calcula diferença em minutos
            ideal_datetime = datetime.combine(datetime.today(), ideal_time)
            duty_datetime = datetime.combine(datetime.today(), duty_type.time)
            difference = abs((ideal_datetime - duty_datetime).total_seconds() / 60)
            
            if min_difference is None or difference < min_difference:
                min_difference = difference
                best_match = duty_type
        
        return best_match

class DutySchedule(models.Model):
    """Escala de responsabilidades"""
    member = models.ForeignKey(TeamMember, on_delete=models.CASCADE)
    duty_type = models.ForeignKey(DutyType, on_delete=models.CASCADE)
    date = models.DateField()
    completed = models.BooleanField(default=False)
    notification_sent = models.BooleanField(default=False)
    coffees_served = models.PositiveIntegerField(default=0, help_text="Quantidade de cafés servidos neste turno")
    notes = models.TextField(blank=True, null=True, help_text="Observações sobre esta escala")
    
    class Meta:
        unique_together = ('duty_type', 'date')
        
    def __str__(self):
        return f"{self.member} - {self.duty_type} - {self.date}"
    
    def is_time_optimal_for_member(self):
        """Verifica se o horário da tarefa é ideal para o membro"""
        ideal_time = self.member.get_cleaning_time()
        duty_time = self.duty_type.time
        
        # Considera ótimo se a diferença for menor que 30 minutos
        ideal_datetime = datetime.combine(datetime.today(), ideal_time)
        duty_datetime = datetime.combine(datetime.today(), duty_time)
        difference_minutes = abs((ideal_datetime - duty_datetime).total_seconds() / 60)
        
        return difference_minutes <= 30
    
    def get_time_difference_display(self):
        """Mostra a diferença entre horário ideal e real"""
        ideal_time = self.member.get_cleaning_time()
        duty_time = self.duty_type.time
        
        ideal_datetime = datetime.combine(datetime.today(), ideal_time)
        duty_datetime = datetime.combine(datetime.today(), duty_time)
        difference = duty_datetime - ideal_datetime
        
        minutes = int(difference.total_seconds() / 60)
        
        if minutes == 0:
            return "Horário ideal"
        elif minutes > 0:
            return f"{minutes}min depois do ideal"
        else:
            return f"{abs(minutes)}min antes do ideal"