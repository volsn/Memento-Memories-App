from celery import shared_task


@shared_task
def delete_expired_memories():
    pass
