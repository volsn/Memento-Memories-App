from celery.schedules import crontab

from .base import *

# Django REST Framework

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20
}

# Celery Configuration Options

CELERY_TIMEZONE = 'Europe/Kiev'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_URL = 'redis://redis:6379'
CELERY_RESULT_BACKEND = 'redis://redis:6379'

CELERY_BEAT_SCHEDULE = {
    'delete_expired_memories': {
        'task': 'memories.tasks.delete_expired_memories',
        'schedule': crontab(minute='*/1'),
    },
}
