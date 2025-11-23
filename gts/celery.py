# celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gts.settings')

app = Celery('gts')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# تنظیمات مخصوص ویندوز
app.conf.update(
    worker_pool='solo',
    worker_concurrency=15,
    task_always_eager=False,
)