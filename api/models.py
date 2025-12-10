from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    rut = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


from .constants import (
    EquipmentCategory,
    TechnicianSpecialty,
    WorkOrderStatus,
    WorkOrderPriority,
)


class Equipment(models.Model):
    empresa = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="equipments"
    )
    nombre = models.CharField(max_length=255)
    serie = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=20,
        choices=EquipmentCategory.choices,
        default=EquipmentCategory.GENERAL,
    )
    critico = models.BooleanField(default=False)
    fecha_instalacion = models.DateField()

    def __str__(self):
        return f"{self.nombre} ({self.serie}) - {self.get_categoria_display()}"


class Technician(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    especialidad = models.CharField(
        max_length=20,
        choices=TechnicianSpecialty.choices,
        default=TechnicianSpecialty.GENERAL,
    )
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} ({self.get_especialidad_display()})"


class MaintenancePlan(models.Model):
    equipo = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="plans"
    )
    nombre = models.CharField(max_length=255)
    frecuencia = models.IntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class WorkOrder(models.Model):
    plan = models.ForeignKey(
        MaintenancePlan, on_delete=models.CASCADE, related_name="work_orders"
    )
    equipo = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="work_orders"
    )
    tecnico = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True
    )
    estado = models.CharField(
        max_length=20, choices=WorkOrderStatus.choices, default=WorkOrderStatus.PENDING
    )
    prioridad = models.CharField(
        max_length=10,
        choices=WorkOrderPriority.choices,
        default=WorkOrderPriority.MEDIA,
    )
    fecha_programada = models.DateField()
    fecha_termino = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Orden #{self.pk} - {self.estado} ({self.prioridad})"
