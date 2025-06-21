"""
Celery configuration for ad_agency project.
"""

import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ad_agency.settings')
app = Celery('ad_agency')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self) -> str:
    print(f'Request: {self.request!r}')
    return 'Celery is working!' 