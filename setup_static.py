#!/usr/bin/env python
"""
Script para configurar e verificar arquivos estáticos do DolceScale
Execute este script para resolver problemas com CSS e JS
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    print("\n" + "="*50)
    print(f" {text}")
    print("="*50)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_warning(text):
    print(f"⚠️  {text}")

def check_django_project():
    """Verifica se estamos em um projeto Django"""
    if not os.path.exists('manage.py'):
        print_error("manage.py não encontrado. Execute este script na raiz do projeto Django.")
        return False
    return True

def create_directories():
    """Cria os diretórios necessários para arquivos estáticos"""
    print_header("CRIANDO DIRETÓRIOS")
    
    directories = [
        'static',
        'static/css',
        'static/js',
        'static/img',
        'staticfiles',
        'media',
        'media/avatars'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print_success(f"Diretório '{directory}' criado/verificado")

def check_static_files():
    """Verifica se os arquivos estáticos existem"""
    print_header("VERIFICANDO ARQUIVOS ESTÁTICOS")
    
    files_to_check = [
        'static/css/main.css',
        'static/js/main.js'
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print_success(f"Arquivo '{file_path}' encontrado")
        else:
            print_error(f"Arquivo '{file_path}' não encontrado")
            missing_files.append(file_path)
    
    return missing_files

def copy_files_from_staticfiles():
    """Copia arquivos da pasta staticfiles para static se necessário"""
    print_header("COPIANDO ARQUIVOS DE STATICFILES")
    
    import shutil
    
    files_to_copy = [
        ('staticfiles/css/main.css', 'static/css/main.css'),
        ('staticfiles/js/main.js', 'static/js/main.js')
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src) and not os.path.exists(dst):
            # Criar diretório de destino se não existir
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            print_success(f"Copiado {src} -> {dst}")
        elif os.path.exists(dst):
            print_success(f"Arquivo {dst} já existe")
        else:
            print_warning(f"Arquivo origem {src} não encontrado")

def run_collectstatic():
    """Executa o comando collectstatic"""
    print_header("EXECUTANDO COLLECTSTATIC")
    
    try:
        result = subprocess.run([
            sys.executable, 'manage.py', 'collectstatic', '--noinput'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("collectstatic executado com sucesso")
            print(result.stdout)
        else:
            print_error("Erro ao executar collectstatic")
            print(result.stderr)
            return False
    except Exception as e:
        print_error(f"Erro ao executar collectstatic: {e}")
        return False
    
    return True

def check_django_settings():
    """Verifica as configurações do Django"""
    print_header("VERIFICANDO CONFIGURAÇÕES DJANGO")
    
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dolcescale.settings')
        import django
        django.setup()
        
        from django.conf import settings
        
        # Verificar configurações importantes
        print_success(f"STATIC_URL: {settings.STATIC_URL}")
        print_success(f"STATIC_ROOT: {settings.STATIC_ROOT}")
        
        if hasattr(settings, 'STATICFILES_DIRS'):
            print_success(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
        else:
            print_warning("STATICFILES_DIRS não configurado")
        
        print_success(f"DEBUG: {settings.DEBUG}")
        
    except Exception as e:
        print_error(f"Erro ao verificar configurações: {e}")
        return False
    
    return True

def test_static_files():
    """Testa se os arquivos estáticos são acessíveis"""
    print_header("TESTANDO ACESSO AOS ARQUIVOS")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Testar arquivos estáticos
        files_to_test = ['/static/css/main.css', '/static/js/main.js']
        
        for file_url in files_to_test:
            try:
                response = client.get(file_url)
                if response.status_code == 200:
                    print_success(f"Arquivo {file_url} acessível (Status: {response.status_code})")
                else:
                    print_error(f"Arquivo {file_url} não acessível (Status: {response.status_code})")
            except Exception as e:
                print_error(f"Erro ao testar {file_url}: {e}")
                
    except Exception as e:
        print_warning(f"Não foi possível testar arquivos: {e}")

def main():
    """Função principal"""
    print_header("DOLCESCALE - CONFIGURADOR DE ARQUIVOS ESTÁTICOS")
    
    # Verificar se estamos no projeto Django
    if not check_django_project():
        return
    
    # Criar diretórios necessários
    create_directories()
    
    # Verificar arquivos estáticos
    missing_files = check_static_files()
    
    # Se arquivos estão faltando, tentar copiar do staticfiles
    if missing_files:
        copy_files_from_staticfiles()
    
    # Verificar configurações Django
    check_django_settings()
    
    # Executar collectstatic
    run_collectstatic()
    
    # Testar arquivos
    test_static_files()
    
    print_header("PRÓXIMOS PASSOS")
    print("1. Execute 'python manage.py runserver' para iniciar o servidor")
    print("2. Acesse http://127.0.0.1:8000 e verifique se CSS/JS carregam")
    print("3. Se ainda houver problemas, verifique o console do navegador")
    print("4. Em caso de dúvidas, verifique os arquivos settings.py e urls.py")
    
    print_header("COMANDOS ÚTEIS")
    print("• python manage.py collectstatic --clear  # Limpa e coleta arquivos estáticos")
    print("• python manage.py runserver 0.0.0.0:8000  # Executa servidor em todas as interfaces")
    print("• python manage.py check --deploy  # Verifica configurações para produção")

if __name__ == '__main__':
    main()