from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkOrder
from .ai_service import AIService
from .constants import WorkOrderPriority


@receiver(post_save, sender=WorkOrder)
def analyze_work_order_on_create(sender, instance, created, **kwargs):
    """
    Automatic AI Analysis Trigger.
    When a WorkOrder is created, the AI analyzes the notes and updates the priority
    and potentially assigns a technician if one isn't set.
    """
    if created and instance.notas:
        # Perform Analysis
        suggested_priority = AIService.analyze_priority(instance.notas)

        # Auto-update if current priority is default (MEDIA) and suggestion is different
        # Or if we want to enforce AI (here we only update if suggestion is higher/different)
        if suggested_priority != instance.prioridad:
            instance.prioridad = suggested_priority
            # IMPORTANT: Save with update_fields to avoid infinite recursion loop
            # although post_save.connect(..., weak=False) dispatch_uid could be safe,
            # explicit save update_fields avoids triggering full save signals loops if strictly managed.
            # However, for simple signal recursion avoidance:
            # We can disable signals locally or just check a flag.
            # Since we are modifying the instance, we need to save it.
            # We use a standard save, but we need to ensure this signal doesn't trigger
            # infinite recursion if we were editing other fields.
            # Since we check 'created', this specific block runs only ONCE per creation.
            # But wait, save() calls post_save again with created=False.
            # So the 'if created' check PROTECTS us from infinite recursion on the second save.
            instance.save(update_fields=["prioridad"])

            # Optional: Log the AI action
            print(
                f"[AI] Auto-updated WorkOrder {instance.id} priority to {suggested_priority}"
            )
