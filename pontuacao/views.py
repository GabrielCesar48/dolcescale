# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Codigo, Pontuacao
from .forms import CodigoForm, ResgatePontosForm


@login_required
def pontuacao_dashboard(request):
    """
    View principal do sistema de pontuação.
    Mostra o saldo de pontos e permite enviar novos códigos.
    """
    if request.method == 'POST':
        form = CodigoForm(request.POST)
        if form.is_valid():
            codigo_texto = form.cleaned_data['codigo'].upper().replace(' ', '')
            
            # Verificar se o código já existe
            if Codigo.objects.filter(codigo=codigo_texto).exists():
                messages.error(request, 'Este código já foi enviado anteriormente.')
            else:
                # Criar novo código
                codigo = Codigo.objects.create(
                    usuario=request.user,
                    codigo=codigo_texto
                )
                messages.success(
                    request, 
                    f'Código {codigo.formatar_codigo()} enviado com sucesso! '
                    'Aguarde a aprovação do administrador.'
                )
                return redirect('pontuacao_dashboard')
    else:
        form = CodigoForm()
    
    # Buscar códigos do usuário
    codigos_usuario = Codigo.objects.filter(usuario=request.user)
    
    # Buscar histórico de pontuação
    historico = Pontuacao.objects.filter(usuario=request.user)
    
    # Paginação
    paginator_codigos = Paginator(codigos_usuario, 10)
    paginator_historico = Paginator(historico, 10)
    
    page_codigos = request.GET.get('page_codigos', 1)
    page_historico = request.GET.get('page_historico', 1)
    
    codigos_page = paginator_codigos.get_page(page_codigos)
    historico_page = paginator_historico.get_page(page_historico)
    
    context = {
        'form': form,
        'saldo_pontos': request.user.saldo_pontos,
        'codigos': codigos_page,
        'historico': historico_page,
        'total_codigos_aprovados': codigos_usuario.filter(status='aprovado').count(),
        'total_codigos_pendentes': codigos_usuario.filter(status='pendente').count(),
    }
    
    return render(request, 'pontuacao/dashboard.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_codigos(request):
    """
    View administrativa para aprovar/rejeitar códigos.
    Apenas administradores têm acesso.
    """
    # Filtros
    status_filter = request.GET.get('status', 'pendente')
    search = request.GET.get('search', '')
    
    codigos = Codigo.objects.all()
    
    if status_filter:
        codigos = codigos.filter(status=status_filter)
    
    if search:
        codigos = codigos.filter(
            Q(codigo__icontains=search) | 
            Q(usuario__username__icontains=search) |
            Q(usuario__email__icontains=search)
        )
    
    # Ordenação
    codigos = codigos.select_related('usuario', 'aprovado_por')
    
    # Paginação
    paginator = Paginator(codigos, 20)
    page = request.GET.get('page', 1)
    codigos_page = paginator.get_page(page)
    
    context = {
        'codigos': codigos_page,
        'status_filter': status_filter,
        'search': search,
        'total_pendentes': Codigo.objects.filter(status='pendente').count(),
    }
    
    return render(request, 'pontuacao/admin_codigos.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def aprovar_codigo(request, codigo_id):
    """
    View para aprovar um código e adicionar pontos ao usuário.
    """
    codigo = get_object_or_404(Codigo, id=codigo_id)
    
    if codigo.status != 'pendente':
        messages.warning(request, 'Este código já foi processado.')
        return redirect('admin_codigos')
    
    # Atualizar status do código
    codigo.status = 'aprovado'
    codigo.data_aprovacao = timezone.now()
    codigo.aprovado_por = request.user
    codigo.save()
    
    # Adicionar pontos ao usuário
    Pontuacao.objects.create(
        usuario=codigo.usuario,
        tipo='adicao',
        pontos=codigo.pontos,
        descricao=f'Código {codigo.formatar_codigo()} aprovado',
        codigo=codigo,
        processado_por=request.user
    )
    
    messages.success(
        request, 
        f'Código {codigo.formatar_codigo()} aprovado com sucesso! '
        f'{codigo.pontos} pontos adicionados para {codigo.usuario.username}.'
    )
    
    return redirect('admin_codigos')


@login_required
@user_passes_test(lambda u: u.is_staff)
def rejeitar_codigo(request, codigo_id):
    """
    View para rejeitar um código.
    """
    codigo = get_object_or_404(Codigo, id=codigo_id)
    
    if codigo.status != 'pendente':
        messages.warning(request, 'Este código já foi processado.')
        return redirect('admin_codigos')
    
    if request.method == 'POST':
        observacoes = request.POST.get('observacoes', '')
        
        codigo.status = 'rejeitado'
        codigo.data_aprovacao = timezone.now()
        codigo.aprovado_por = request.user
        codigo.observacoes = observacoes
        codigo.save()
        
        messages.success(
            request, 
            f'Código {codigo.formatar_codigo()} rejeitado.'
        )
        
        return redirect('admin_codigos')
    
    return render(request, 'pontuacao/rejeitar_codigo.html', {'codigo': codigo})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_usuarios_pontos(request):
    """
    View para gerenciar pontos dos usuários (resgates).
    """
    search = request.GET.get('search', '')
    
    # Buscar usuários com pontos
    from django.contrib.auth.models import User
    from django.db.models import Sum, Q
    
    usuarios = User.objects.annotate(
        saldo=Sum('pontuacoes__pontos', default=0)
    ).filter(saldo__gt=0)
    
    if search:
        usuarios = usuarios.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    usuarios = usuarios.order_by('-saldo')
    
    # Paginação
    paginator = Paginator(usuarios, 20)
    page = request.GET.get('page', 1)
    usuarios_page = paginator.get_page(page)
    
    context = {
        'usuarios': usuarios_page,
        'search': search,
    }
    
    return render(request, 'pontuacao/admin_usuarios_pontos.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
@transaction.atomic
def resgatar_pontos(request, user_id):
    """
    View para resgatar (zerar) pontos de um usuário.
    """
    from django.contrib.auth.models import User
    usuario = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = ResgatePontosForm(request.POST, usuario=usuario)
        if form.is_valid():
            pontos_resgate = form.cleaned_data['pontos']
            descricao = form.cleaned_data['descricao']
            
            # Criar transação de resgate (pontos negativos)
            Pontuacao.objects.create(
                usuario=usuario,
                tipo='resgate',
                pontos=-pontos_resgate,  # Negativo para subtrair
                descricao=descricao,
                processado_por=request.user
            )
            
            messages.success(
                request,
                f'{pontos_resgate} pontos resgatados com sucesso para {usuario.username}. '
                f'Novo saldo: {usuario.saldo_pontos} pontos.'
            )
            
            return redirect('admin_usuarios_pontos')
    else:
        form = ResgatePontosForm(usuario=usuario)
    
    context = {
        'form': form,
        'usuario': usuario,
        'saldo_atual': usuario.saldo_pontos,
    }
    
    return render(request, 'pontuacao/resgatar_pontos.html', context)