"""
WSGI config for backend_core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from auto_migrate import run_migrations  # import 

# Run migrations once on startup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_core.settings')

application = get_wsgi_application()

run_migrations()
