from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OT
from .services import ServIA


@receiver(post_save, sender=OT)
def crear_ot(sender, instance, created, **kwargs):
    """
    Al Crear (crear_ot). Usa ServIA.
    """
    if created and instance.notas:
        # Calc P
        p_a = ServIA.calc_p(instance.notas)

        if p_a != instance.prioridad:
            instance.prioridad = p_a
            instance.save(update_fields=["prioridad"])
            print(f"[IA] Act OT {instance.id} -> {p_a}")
