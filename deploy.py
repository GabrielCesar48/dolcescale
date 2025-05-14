#!/usr/bin/env python
import os
import subprocess

# Colete arquivos estáticos
print("Coletando arquivos estáticos...")
subprocess.call(['python', 'manage.py', 'collectstatic', '--noinput'])

# Aplique migrações
print("Aplicando migrações...")
subprocess.call(['python', 'manage.py', 'migrate', '--noinput'])

# Verifique por erros
print("Verificando por erros...")
subprocess.call(['python', 'manage.py', 'check', '--deploy'])

print("Deploy preparado com sucesso!")