from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TeamMember(models.Model):
    """Modelo para membros da equipe de TI"""
    email = models.EmailField(unique=True, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, help_text="Número de WhatsApp", null=True, blank=True) 
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Holiday(models.Model):
    """Modelo para feriados"""
    date = models.DateField(unique=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.name} ({self.date})"

class DutyType(models.Model):
    """Tipo de tarefa (reabastecimento matinal ou limpeza vespertina)"""
    name = models.CharField(max_length=50)
    time = models.TimeField()  # Horário da tarefa
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name} ({self.time})"

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