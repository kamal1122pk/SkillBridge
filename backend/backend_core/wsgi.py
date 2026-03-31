import os
from auto_migrate import run_migrations  # your migration runner

# Set Django settings module first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_core.settings')

# Run migrations before loading WSGI application
run_migrations()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()