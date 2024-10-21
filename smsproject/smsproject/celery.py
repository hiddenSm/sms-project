from __future__ import absolute_import, unicode_literals
import os, sentry_sdk
from celery import Celery
from django.conf import settings
from sentry_sdk.integrations.celery import CeleryIntegration

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smsproject.settings')

sentry_sdk.init(
    dsn="https://758db00baea4459cb0bb628dca4fb841@o4507849364340736.ingest.de.sentry.io/4507967444353104",
    integrations=[CeleryIntegration()],
    traces_sample_rate=1.0,
)

# Create a Celery instance
app = Celery('smsproject')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')
# app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery will auto-discover tasks from installed apps
# app.autodiscover_tasks()
app.autodiscover_tasks(lambda:settings.INSTALLED_APPS)


app.conf.timezone = 'Asia/Tehran'  # Replace with your desired timezone

# Enable UTC
app.conf.enable_utc = True