from django.db import models
from django.contrib.auth.models import User
from .constants import CE, ET, EO, PO


class Emp(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    rut = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class Eq(models.Model):
    empresa = models.ForeignKey(
        Emp, on_delete=models.CASCADE, related_name="equipments"
    )
    nombre = models.CharField(max_length=255)
    serie = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CE.choices, default=CE.GRAL)
    critico = models.BooleanField(default=False)
    fecha_instalacion = models.DateField()

    def __str__(self):
        return f"{self.nombre} ({self.serie}) - {self.get_categoria_display()}"


class Tec(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    especialidad = models.CharField(max_length=20, choices=ET.choices, default=ET.GRAL)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} ({self.get_especialidad_display()})"


class PM(models.Model):
    equipo = models.ForeignKey(Eq, on_delete=models.CASCADE, related_name="plans")
    nombre = models.CharField(max_length=255)
    frecuencia = models.IntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class OT(models.Model):
    plan = models.ForeignKey(PM, on_delete=models.CASCADE, related_name="work_orders")
    equipo = models.ForeignKey(Eq, on_delete=models.CASCADE, related_name="work_orders")
    tecnico = models.ForeignKey(Tec, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=EO.choices, default=EO.PEND)
    prioridad = models.CharField(max_length=10, choices=PO.choices, default=PO.MEDI)
    fecha_programada = models.DateField()
    fecha_termino = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"OT #{self.pk} - {self.estado} ({self.prioridad})"
