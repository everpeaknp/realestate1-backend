"""
ASGI config for realtor_pal project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'realtor_pal.settings')

application = get_asgi_application()
