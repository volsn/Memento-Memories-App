from django.db.models.signals import post_delete
from django.dispatch import receiver

from core.models import Memory


@receiver(post_delete, sender=Memory)
def notify_user(sender, **kwargs):
    print(sender)
