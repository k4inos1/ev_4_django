from django.contrib.auth.models import User
from django.db import models

from .constants import CE, EO, ET, PO

# modelos hiper-densos (opt bytes)


class Gen(models.Model):
    """adn config."""

    adn = models.JSONField(default=dict)
    hsh = models.CharField(max_length=64)


class Emp(models.Model):
    nom = models.CharField(max_length=50)
    dir = models.CharField(max_length=50)
    rut = models.CharField(max_length=12)
    t_c = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class Eq(models.Model):
    emp = models.ForeignKey(Emp, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    ser = models.CharField(max_length=50)
    cat = models.IntegerField(choices=CE.choices, default=CE.GR)
    cri = models.BooleanField(default=False)
    t_i = models.DateField()
    gen = models.OneToOneField(Gen, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nom}:{self.cat}"


class Nodo(models.Model):
    """telemetria 4-8 bytes."""

    uid = models.UUIDField(primary_key=True)
    eq = models.ForeignKey(Eq, on_delete=models.CASCADE)
    tip = models.IntegerField(default=1)  # 1=vibr, 2=temp
    lec = models.FloatField(default=0.0)
    t_u = models.DateTimeField(auto_now=True)


class Tec(models.Model):
    usr = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    esp = models.IntegerField(choices=ET.choices, default=ET.GR)
    tel = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


class PM(models.Model):
    eq = models.ForeignKey(Eq, on_delete=models.CASCADE)
    nom = models.CharField(max_length=50)
    frq = models.IntegerField()
    on = models.BooleanField(default=True)


class Flux(models.Model):
    """estado de proceso (bitmask)."""

    cla = models.CharField(max_length=10)  # clave
    st = models.IntegerField(default=0)


class OT(models.Model):
    pln = models.ForeignKey(PM, on_delete=models.CASCADE)
    eq = models.ForeignKey(Eq, on_delete=models.CASCADE)
    tec = models.ForeignKey(
        Tec, on_delete=models.SET_NULL, null=True, blank=True, related_name="wos"
    )
    st = models.IntegerField(choices=EO.choices, default=EO.PEND)
    pr = models.IntegerField(choices=PO.choices, default=PO.MEDI)
    t_p = models.DateField()
    t_e = models.DateTimeField(null=True, blank=True)
    n = models.TextField(blank=True)  # notas

    def __str__(self):
        return f"#{self.pk}:{self.st}"


class Repuesto(models.Model):
    """repuestos/inventario."""

    cod = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    stock = models.IntegerField(default=0)
    min = models.IntegerField(default=5)  # stock minimo
    eq = models.ForeignKey(Eq, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.cod}:{self.stock}"


class Proveedor(models.Model):
    """proveedores."""

    nom = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    tel = models.CharField(max_length=20)
    rating = models.IntegerField(default=3)  # 1-5

    def __str__(self):
        return self.nom


class Inspeccion(models.Model):
    """inspecciones/auditorias."""

    eq = models.ForeignKey(Eq, on_delete=models.CASCADE)
    tec = models.ForeignKey(Tec, on_delete=models.SET_NULL, null=True)
    t_i = models.DateTimeField(auto_now_add=True)
    resultado = models.JSONField(default=dict)
    aprobado = models.BooleanField(default=False)

    def __str__(self):
        return f"insp:{self.eq.nom}:{self.aprobado}"


class Incidente(models.Model):
    """incidentes/fallas."""

    eq = models.ForeignKey(Eq, on_delete=models.CASCADE)
    t_i = models.DateTimeField(auto_now_add=True)
    severidad = models.IntegerField(default=5)  # 1-10
    desc = models.TextField()
    resuelto = models.BooleanField(default=False)

    def __str__(self):
        return f"inc:{self.eq.nom}:sev{self.severidad}"
