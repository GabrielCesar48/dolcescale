# pontuacao/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class PontuacaoAuthMiddleware:
    """
    Middleware para garantir que apenas usuários autenticados
    acessem o sistema de pontuação.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # URLs que começam com /pontuacao/
        if request.path.startswith('/pontuacao/'):
            if not request.user.is_authenticated:
                # Redirecionar para login salvando a URL de destino
                login_url = f"{reverse('login')}?next={request.path}"
                return redirect(login_url)
        
        response = self.get_response(request)
        return response


# Adicionar ao settings.py do projeto Django:
"""
# No arquivo settings.py, adicione o middleware à lista MIDDLEWARE:

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Adicione o middleware do sistema de pontuação
    'pontuacao.middleware.PontuacaoAuthMiddleware',
]

# Configurações de autenticação
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/pontuacao/'
LOGOUT_REDIRECT_URL = '/login/'

# Se você ainda não tem views de login/logout, adicione ao urls.py principal:
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ... outras URLs
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
"""

# Template de login simples - criar em templates/login.html
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Sistema de Pontuação</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .login-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .login-header i {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        
        .btn-login {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            padding: 12px 30px;
            font-weight: 500;
            transition: transform 0.2s;
        }
        
        .btn-login:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="login-header">
            <i class="fas fa-coins"></i>
            <h3>Sistema de Pontuação</h3>
            <p class="text-muted">Faça login para continuar</p>
        </div>
        
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% if form.errors %}
            <div class="alert alert-danger">
                Por favor, corrija os erros abaixo.
            </div>
        {% endif %}
        
        <form method="post">
            {% csrf_token %}
            <div class="mb-3">
                <label for="id_username" class="form-label">
                    <i class="fas fa-user"></i> Usuário
                </label>
                <input type="text" class="form-control" name="username" id="id_username" 
                       required autofocus placeholder="Digite seu usuário">
            </div>
            
            <div class="mb-4">
                <label for="id_password" class="form-label">
                    <i class="fas fa-lock"></i> Senha
                </label>
                <input type="password" class="form-control" name="password" id="id_password" 
                       required placeholder="Digite sua senha">
            </div>
            
            {% if next %}
                <input type="hidden" name="next" value="{{ next }}">
            {% endif %}
            
            <div class="d-grid">
                <button type="submit" class="btn btn-login btn-lg">
                    <i class="fas fa-sign-in-alt"></i> Entrar
                </button>
            </div>
        </form>
        
        <hr class="my-4">
        
        <p class="text-center text-muted mb-0">
            <small>Sistema de Pontuação &copy; {% now "Y" %}</small>
        </p>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""