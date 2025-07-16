# models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db.models import Sum

class Codigo(models.Model):
    """
    Model para armazenar os códigos enviados pelos usuários.
    Cada código tem 12 caracteres alfanuméricos em maiúsculas.
    """
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]
    
    codigo_validator = RegexValidator(
        regex=r'^[A-Z0-9]{12}$',
        message='O código deve conter exatamente 12 caracteres alfanuméricos em maiúsculas.'
    )
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='codigos')
    codigo = models.CharField(
        max_length=12, 
        validators=[codigo_validator],
        unique=True,
        help_text='Código de 12 caracteres em maiúsculas'
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='pendente'
    )
    pontos = models.IntegerField(default=100)
    data_envio = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    aprovado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='codigos_aprovados'
    )
    observacoes = models.TextField(blank=True, help_text='Observações do administrador')
    
    class Meta:
        ordering = ['-data_envio']
        verbose_name = 'Código'
        verbose_name_plural = 'Códigos'
        
    def __str__(self):
        return f'{self.codigo} - {self.usuario.username} - {self.status}'
    
    def formatar_codigo(self):
        """Retorna o código formatado com espaços: XXXX XXXX XXXX"""
        return f'{self.codigo[:4]} {self.codigo[4:8]} {self.codigo[8:12]}'


class Pontuacao(models.Model):
    """
    Model para controlar a pontuação dos usuários.
    Mantém um registro histórico de todas as transações de pontos.
    """
    TIPO_CHOICES = [
        ('adicao', 'Adição'),
        ('resgate', 'Resgate'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pontuacoes')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    pontos = models.IntegerField()
    descricao = models.CharField(max_length=200)
    codigo = models.ForeignKey(
        Codigo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='transacoes_pontos'
    )
    data = models.DateTimeField(auto_now_add=True)
    processado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pontuacoes_processadas'
    )
    
    class Meta:
        ordering = ['-data']
        verbose_name = 'Pontuação'
        verbose_name_plural = 'Pontuações'
        
    def __str__(self):
        return f'{self.usuario.username} - {self.tipo} - {self.pontos} pontos'


# Adicionar método ao modelo User para calcular saldo de pontos
def calcular_saldo_pontos(self):
    """
    Calcula o saldo atual de pontos do usuário.
    Soma todas as adições e subtrai todos os resgates.
    """
    total = self.pontuacoes.aggregate(
        saldo=Sum('pontos', default=0)
    )['saldo']
    return total or 0

# Adicionar método como propriedade do User
User.add_to_class('saldo_pontos', property(calcular_saldo_pontos))