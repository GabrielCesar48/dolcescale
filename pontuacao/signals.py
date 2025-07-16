# pontuacao/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Codigo, Pontuacao


@receiver(post_save, sender=Codigo)
def notificar_status_codigo(sender, instance, created, **kwargs):
    """
    Sinal para notificar o usuário quando o status do código mudar.
    Pode ser usado para enviar email ou outras notificações.
    """
    if not created and instance.status in ['aprovado', 'rejeitado']:
        # Aqui você pode implementar o envio de email
        # Por exemplo:
        """
        subject = f'Código {instance.formatar_codigo()} - {instance.get_status_display()}'
        
        if instance.status == 'aprovado':
            message = f'''
            Olá {instance.usuario.get_full_name() or instance.usuario.username},
            
            Seu código {instance.formatar_codigo()} foi aprovado!
            Você recebeu {instance.pontos} pontos.
            
            Seu saldo atual é de {instance.usuario.saldo_pontos} pontos.
            
            Atenciosamente,
            Sistema de Pontuação
            '''
        else:
            message = f'''
            Olá {instance.usuario.get_full_name() or instance.usuario.username},
            
            Infelizmente, seu código {instance.formatar_codigo()} foi rejeitado.
            
            {f"Motivo: {instance.observacoes}" if instance.observacoes else ""}
            
            Atenciosamente,
            Sistema de Pontuação
            '''
        
        # Enviar email (descomente se configurado)
        # send_mail(
        #     subject,
        #     message,
        #     settings.DEFAULT_FROM_EMAIL,
        #     [instance.usuario.email],
        #     fail_silently=True,
        # )
        """
        pass


@receiver(post_save, sender=Pontuacao)
def notificar_transacao_pontos(sender, instance, created, **kwargs):
    """
    Sinal para notificar quando houver transação de pontos.
    Útil para manter logs ou enviar notificações.
    """
    if created:
        # Log da transação
        print(f"Nova transação de pontos: {instance}")
        
        # Aqui você pode adicionar outras ações como:
        # - Verificar marcos de pontuação (ex: usuário atingiu 1000 pontos)
        # - Atualizar badges ou conquistas
        # - Enviar notificações push
        
        # Exemplo de verificação de marco
        saldo_atual = instance.usuario.saldo_pontos
        
        marcos = [100, 500, 1000, 5000, 10000]
        for marco in marcos:
            if saldo_atual >= marco and (saldo_atual - abs(instance.pontos)) < marco:
                # Usuário acabou de atingir um marco
                print(f"Usuário {instance.usuario.username} atingiu {marco} pontos!")
                # Aqui você pode criar um sistema de conquistas/badges


# pontuacao/apps.py
from django.apps import AppConfig


class PontuacaoConfig(AppConfig):
    """
    Configuração do app Pontuação.
    Registra os signals quando o app é carregado.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pontuacao'
    verbose_name = 'Sistema de Pontuação'
    
    def ready(self):
        """
        Importa os signals quando o app está pronto.
        """
        import pontuacao.signals


# pontuacao/__init__.py
# Certifique-se de que o app use a configuração correta
default_app_config = 'pontuacao.apps.PontuacaoConfig'