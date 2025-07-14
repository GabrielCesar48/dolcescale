# core/management/commands/check_static.py

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
import os
from pathlib import Path

class Command(BaseCommand):
    help = 'Verifica a configuração e disponibilidade dos arquivos estáticos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Tenta corrigir problemas encontrados'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Verificando configuração de arquivos estáticos...\n'))
        
        # Verificar configurações
        self.check_settings()
        
        # Verificar diretórios
        self.check_directories()
        
        # Verificar arquivos principais
        self.check_main_files(fix=options['fix'])
        
        # Verificar finders
        self.check_finders()
        
        # Verificar URLs
        self.check_urls()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Verificação concluída!'))

    def check_settings(self):
        """Verifica as configurações relacionadas a arquivos estáticos"""
        self.stdout.write(self.style.WARNING('📋 Verificando configurações:'))
        
        # STATIC_URL
        self.stdout.write(f'   STATIC_URL: {settings.STATIC_URL}')
        
        # STATIC_ROOT
        self.stdout.write(f'   STATIC_ROOT: {settings.STATIC_ROOT}')
        
        # STATICFILES_DIRS
        if hasattr(settings, 'STATICFILES_DIRS'):
            self.stdout.write(f'   STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
        else:
            self.stdout.write(self.style.ERROR('   STATICFILES_DIRS: Não configurado'))
        
        # DEBUG
        self.stdout.write(f'   DEBUG: {settings.DEBUG}')
        
        print()

    def check_directories(self):
        """Verifica se os diretórios existem"""
        self.stdout.write(self.style.WARNING('📁 Verificando diretórios:'))
        
        directories = []
        
        # STATIC_ROOT
        if settings.STATIC_ROOT:
            directories.append(('STATIC_ROOT', settings.STATIC_ROOT))
        
        # STATICFILES_DIRS
        if hasattr(settings, 'STATICFILES_DIRS'):
            for i, static_dir in enumerate(settings.STATICFILES_DIRS):
                directories.append((f'STATICFILES_DIRS[{i}]', static_dir))
        
        for name, directory in directories:
            if os.path.exists(directory):
                self.stdout.write(f'   ✅ {name}: {directory}')
            else:
                self.stdout.write(f'   ❌ {name}: {directory} (não existe)')
        
        print()

    def check_main_files(self, fix=False):
        """Verifica os arquivos CSS e JS principais"""
        self.stdout.write(self.style.WARNING('📄 Verificando arquivos principais:'))
        
        main_files = [
            'css/main.css',
            'js/main.js'
        ]
        
        for file_path in main_files:
            # Usar o finder do Django para localizar o arquivo
            found_file = finders.find(file_path)
            
            if found_file:
                self.stdout.write(f'   ✅ {file_path}: {found_file}')
            else:
                self.stdout.write(f'   ❌ {file_path}: Não encontrado')
                
                if fix:
                    self.try_fix_file(file_path)
        
        print()

    def try_fix_file(self, file_path):
        """Tenta corrigir um arquivo ausente"""
        self.stdout.write(f'   🔧 Tentando corrigir {file_path}...')
        
        # Verificar se existe em staticfiles
        if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
            static_dir = settings.STATICFILES_DIRS[0]
            target_path = os.path.join(static_dir, file_path)
            
            if settings.STATIC_ROOT:
                source_path = os.path.join(settings.STATIC_ROOT, file_path)
                
                if os.path.exists(source_path):
                    # Criar diretório se necessário
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    
                    # Copiar arquivo
                    import shutil
                    shutil.copy2(source_path, target_path)
                    
                    self.stdout.write(f'   ✅ Arquivo copiado para {target_path}')
                    return
            
            # Se não encontrou, criar arquivo básico
            self.create_basic_file(target_path, file_path)

    def create_basic_file(self, target_path, file_path):
        """Cria um arquivo básico se não existir"""
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        if file_path.endswith('.css'):
            content = """/* main.css - DolceScale */
:root {
    --coffee-dark: #3A2618;
    --coffee-medium: #6F4E37;
    --coffee-light: #9B7653;
    --cream: #FFFDD0;
}

body {
    font-family: 'Poppins', sans-serif;
    background-color: #f8f9fa;
}

.btn-coffee {
    background-color: var(--coffee-medium);
    color: white;
}

.navbar {
    background-color: var(--coffee-dark);
}
"""
        elif file_path.endswith('.js'):
            content = """// main.js - DolceScale
document.addEventListener('DOMContentLoaded', function() {
    console.log('DolceScale loaded successfully!');
});
"""
        else:
            content = ""
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.stdout.write(f'   ✅ Arquivo básico criado em {target_path}')

    def check_finders(self):
        """Verifica os finders de arquivos estáticos"""
        self.stdout.write(self.style.WARNING('🔍 Verificando finders:'))
        
        from django.contrib.staticfiles.finders import get_finders
        
        for finder in get_finders():
            finder_name = finder.__class__.__name__
            self.stdout.write(f'   ✅ {finder_name}: Ativo')
        
        print()

    def check_urls(self):
        """Verifica as configurações de URLs"""
        self.stdout.write(self.style.WARNING('🌐 Verificando URLs:'))
        
        # Verificar se está em DEBUG
        if settings.DEBUG:
            self.stdout.write('   ✅ Mode DEBUG ativado - arquivos estáticos servidos pelo Django')
        else:
            self.stdout.write('   ⚠️  Mode PRODUCTION - configure servidor web para servir arquivos estáticos')
        
        print()