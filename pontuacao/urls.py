# pontuacao/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs do usuário
    path('', views.pontuacao_dashboard, name='pontuacao_dashboard'),
    
    # URLs administrativas
    path('admin/codigos/', views.admin_codigos, name='admin_codigos'),
    path('admin/aprovar/<int:codigo_id>/', views.aprovar_codigo, name='aprovar_codigo'),
    path('admin/rejeitar/<int:codigo_id>/', views.rejeitar_codigo, name='rejeitar_codigo'),
    path('admin/usuarios/', views.admin_usuarios_pontos, name='admin_usuarios_pontos'),
    path('admin/resgatar/<int:user_id>/', views.resgatar_pontos, name='resgatar_pontos'),
]