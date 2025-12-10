from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    rut = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class Equipment(models.Model):
    empresa = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="equipments"
    )
    nombre = models.CharField(max_length=255)
    serie = models.CharField(max_length=100)
    critico = models.BooleanField(default=False)
    fecha_instalacion = models.DateField()

    def __str__(self):
        return f"{self.nombre} ({self.serie})"


class Technician(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    especialidad = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


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
    ESTADO_CHOICES = [
        ("PENDING", "Pendiente"),
        ("IN_PROGRESS", "En Progreso"),
        ("COMPLETED", "Completado"),
        ("CANCELLED", "Cancelado"),
    ]
    plan = models.ForeignKey(
        MaintenancePlan, on_delete=models.CASCADE, related_name="work_orders"
    )
    equipo = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="work_orders"
    )
    tecnico = models.ForeignKey(
        Technician, on_delete=models.SET_NULL, null=True, blank=True
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="PENDING")
    fecha_programada = models.DateField()
    fecha_termino = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"Orden #{self.pk} - {self.estado}"
