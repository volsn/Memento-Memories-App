from celery import shared_task

from core.models import Memory


@shared_task
def delete_expired_memories() -> None:
    """Delete memories that have expired"""
    Memory.objects.delete_expired_objects()
