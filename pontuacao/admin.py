# admin.py
from django.contrib import admin
from django.utils import timezone
from django.db import transaction
from .models import Codigo, Pontuacao


@admin.register(Codigo)
class CodigoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Codigo.
    Permite gerenciar códigos diretamente pelo Django Admin.
    """
    list_display = ['formatar_codigo', 'usuario', 'status', 'pontos', 'data_envio', 'aprovado_por']
    list_filter = ['status', 'data_envio', 'data_aprovacao']
    search_fields = ['codigo', 'usuario__username', 'usuario__email']
    readonly_fields = ['data_envio', 'formatar_codigo']
    date_hierarchy = 'data_envio'
    
    fieldsets = (
        ('Informações do Código', {
            'fields': ('codigo', 'formatar_codigo', 'usuario', 'pontos')
        }),
        ('Status', {
            'fields': ('status', 'observacoes')
        }),
        ('Aprovação', {
            'fields': ('aprovado_por', 'data_aprovacao'),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('data_envio',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['aprovar_codigos', 'rejeitar_codigos']
    
    def save_model(self, request, obj, form, change):
        """
        Sobrescreve o save_model para adicionar pontos quando um código é aprovado.
        """
        if change:  # Se está editando um código existente
            old_obj = Codigo.objects.get(pk=obj.pk)
            
            # Se o status mudou para aprovado
            if old_obj.status != 'aprovado' and obj.status == 'aprovado':
                obj.aprovado_por = request.user
                obj.data_aprovacao = timezone.now()
                
                # Adicionar pontos ao usuário
                with transaction.atomic():
                    super().save_model(request, obj, form, change)
                    
                    Pontuacao.objects.create(
                        usuario=obj.usuario,
                        tipo='adicao',
                        pontos=obj.pontos,
                        descricao=f'Código {obj.formatar_codigo()} aprovado',
                        codigo=obj,
                        processado_por=request.user
                    )
                return
        
        super().save_model(request, obj, form, change)
    
    @admin.action(description='Aprovar códigos selecionados')
    def aprovar_codigos(self, request, queryset):
        """
        Ação em lote para aprovar múltiplos códigos.
        """
        codigos_pendentes = queryset.filter(status='pendente')
        count = 0
        
        with transaction.atomic():
            for codigo in codigos_pendentes:
                codigo.status = 'aprovado'
                codigo.aprovado_por = request.user
                codigo.data_aprovacao = timezone.now()
                codigo.save()
                
                Pontuacao.objects.create(
                    usuario=codigo.usuario,
                    tipo='adicao',
                    pontos=codigo.pontos,
                    descricao=f'Código {codigo.formatar_codigo()} aprovado',
                    codigo=codigo,
                    processado_por=request.user
                )
                count += 1
        
        self.message_user(request, f'{count} código(s) aprovado(s) com sucesso.')
    
    @admin.action(description='Rejeitar códigos selecionados')
    def rejeitar_codigos(self, request, queryset):
        """
        Ação em lote para rejeitar múltiplos códigos.
        """
        codigos_pendentes = queryset.filter(status='pendente')
        count = codigos_pendentes.update(
            status='rejeitado',
            aprovado_por=request.user,
            data_aprovacao=timezone.now()
        )
        
        self.message_user(request, f'{count} código(s) rejeitado(s).')


@admin.register(Pontuacao)
class PontuacaoAdmin(admin.ModelAdmin):
    """
    Configuração do admin para o modelo Pontuacao.
    Permite visualizar o histórico de pontuação dos usuários.
    """
    list_display = ['usuario', 'tipo', 'pontos_formatados', 'descricao', 'data', 'processado_por']
    list_filter = ['tipo', 'data', 'processado_por']
    search_fields = ['usuario__username', 'usuario__email', 'descricao']
    readonly_fields = ['usuario', 'tipo', 'pontos', 'descricao', 'codigo', 'data', 'processado_por']
    date_hierarchy = 'data'
    
    def pontos_formatados(self, obj):
        """
        Formata a exibição dos pontos com sinal de + ou -.
        """
        if obj.pontos > 0:
            return f'+{obj.pontos}'
        return str(obj.pontos)
    pontos_formatados.short_description = 'Pontos'
    
    def has_add_permission(self, request):
        """
        Desabilita a adição manual de pontuação via admin.
        As pontuações devem ser criadas apenas através do sistema.
        """
        return False
    
    def has_delete_permission(self, request, obj=None):
        """
        Desabilita a exclusão de pontuações para manter o histórico íntegro.
        """
        return False
    
    def has_change_permission(self, request, obj=None):
        """
        Desabilita a edição de pontuações para manter o histórico íntegro.
        """
        return False