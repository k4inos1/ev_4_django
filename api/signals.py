from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OT
from .servicios import ServOT


@receiver(post_save, sender=OT)
def init_ot(sender, instance, created, **kwargs):
    """inicializa ot (hook)."""
    if created and instance.n:
        # sinc prioridad
        p_old = instance.pr
        ServOT.sinc(instance)

        if instance.pr != p_old:
            instance.save(update_fields=["pr"])
            print(f"[IA] OT#{instance.pk} :: {p_old}->{instance.pr}")
