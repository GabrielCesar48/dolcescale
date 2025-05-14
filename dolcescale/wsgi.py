"""
WSGI config for dolcescale project.
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Adicione o caminho do projeto ao PATH do Python
path = str(Path(__file__).resolve().parent.parent)
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dolcescale.settings')

application = get_wsgi_application()