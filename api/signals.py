from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import WorkOrder
from .models import WorkOrder


@receiver(post_save, sender=WorkOrder)
def auto_complete_timestamp(sender, instance, created, **kwargs):
    # Logic: if status is COMPLETED and completed_at is not set.
    if instance.status == "COMPLETED" and not instance.completed_at:
        instance.completed_at = timezone.now()
        instance.save(update_fields=["completed_at"])
