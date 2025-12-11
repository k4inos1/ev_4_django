from django.db.models.signals import post_save
from django.dispatch import receiver
from api.models import Mantenimiento

@receiver(post_save, sender=Mantenimiento)
def auto_learning_hook(sender, instance, **kwargs):
    if instance.estado == 'completado':
        from api.servicios.ia_core import ia_sistema
        try:
            ia_sistema.auto_aprender(instance, {'fue_exitoso': True})
        except: pass
