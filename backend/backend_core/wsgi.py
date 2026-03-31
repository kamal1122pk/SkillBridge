import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_core.settings')

# Run migrations (careful: every cold start!)
call_command("migrate", interactive=False)

application = get_wsgi_application()