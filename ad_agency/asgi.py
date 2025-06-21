"""
ASGI config for ad_agency project.
"""

import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ad_agency.settings')
application = get_asgi_application() 