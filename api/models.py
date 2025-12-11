from django.db import models
from .constants import CategoriaEquipo, EspecialidadTecnico, EstadoOrden, Prioridad


class Equipo(models.Model):
    """Equipo industrial con información de empresa integrada"""

    nombre = models.CharField(max_length=100, verbose_name="Nombre del equipo")
    empresa_nombre = models.CharField(max_length=100, verbose_name="Empresa")
    categoria = models.IntegerField(
        choices=CategoriaEquipo.choices, verbose_name="Categoría"
    )
    es_critico = models.BooleanField(default=False, verbose_name="¿Es crítico?")
    numero_serie = models.CharField(
        max_length=50, unique=True, verbose_name="Número de serie"
    )
    ubicacion = models.CharField(max_length=200, verbose_name="Ubicación")
    estado = models.CharField(max_length=20, default="operativo", verbose_name="Estado")
    metadatos = models.JSONField(default=dict, verbose_name="Metadatos adicionales")
    fecha_instalacion = models.DateTimeField(verbose_name="Fecha de instalación")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "equipo"
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"
        ordering = ["-es_critico", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.empresa_nombre})"


class Mantenimiento(models.Model):
    """Actividad de mantenimiento (preventivo, correctivo, inspección)"""

    TIPO_PREVENTIVO = "preventivo"
    TIPO_CORRECTIVO = "correctivo"
    TIPO_INSPECCION = "inspeccion"

    TIPOS = [
        (TIPO_PREVENTIVO, "Mantenimiento Preventivo"),
        (TIPO_CORRECTIVO, "Mantenimiento Correctivo"),
        (TIPO_INSPECCION, "Inspección"),
    ]

    equipo = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, related_name="mantenimientos"
    )
    tipo = models.CharField(max_length=20, choices=TIPOS, verbose_name="Tipo")
    prioridad = models.IntegerField(choices=Prioridad.choices, verbose_name="Prioridad")
    estado = models.IntegerField(
        choices=EstadoOrden.choices, default=1, verbose_name="Estado"
    )
    tecnico_asignado = models.CharField(
        max_length=100, blank=True, verbose_name="Técnico"
    )
    fecha_programada = models.DateTimeField(verbose_name="Fecha programada")
    fecha_completada = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha completada"
    )
    descripcion = models.TextField(verbose_name="Descripción")
    resultado = models.TextField(blank=True, verbose_name="Resultado")
    costo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Costo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "mantenimiento"
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ["-prioridad", "fecha_programada"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.equipo.nombre}"


class Recurso(models.Model):
    """Recurso del sistema (técnico, repuesto, proveedor)"""

    TIPO_TECNICO = "tecnico"
    TIPO_REPUESTO = "repuesto"
    TIPO_PROVEEDOR = "proveedor"

    TIPOS = [
        (TIPO_TECNICO, "Técnico"),
        (TIPO_REPUESTO, "Repuesto"),
        (TIPO_PROVEEDOR, "Proveedor"),
    ]

    tipo = models.CharField(
        max_length=20, choices=TIPOS, verbose_name="Tipo de recurso"
    )
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    especialidad = models.CharField(
        max_length=50, blank=True, verbose_name="Especialidad"
    )
    stock = models.IntegerField(default=0, verbose_name="Stock disponible")
    stock_minimo = models.IntegerField(default=0, verbose_name="Stock mínimo")
    contacto = models.CharField(max_length=200, blank=True, verbose_name="Contacto")
    disponible = models.BooleanField(default=True, verbose_name="¿Disponible?")
    calificacion = models.FloatField(default=5.0, verbose_name="Calificación")
    metadatos = models.JSONField(default=dict, verbose_name="Metadatos")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recurso"
        verbose_name = "Recurso"
        verbose_name_plural = "Recursos"
        ordering = ["tipo", "nombre"]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre}"

    @property
    def necesita_reposicion(self):
        """Indica si el stock está por debajo del mínimo"""
        return (
            self.stock < self.stock_minimo if self.tipo == self.TIPO_REPUESTO else False
        )


class Evento(models.Model):
    """Evento del sistema (incidente, telemetría IoT, flujo de proceso)"""

    TIPO_INCIDENTE = "incidente"
    TIPO_TELEMETRIA = "telemetria"
    TIPO_FLUJO = "flujo"

    TIPOS = [
        (TIPO_INCIDENTE, "Incidente"),
        (TIPO_TELEMETRIA, "Telemetría IoT"),
        (TIPO_FLUJO, "Flujo de Proceso"),
    ]

    tipo = models.CharField(max_length=20, choices=TIPOS, verbose_name="Tipo de evento")
    equipo = models.ForeignKey(
        Equipo, on_delete=models.CASCADE, null=True, blank=True, related_name="eventos"
    )
    severidad = models.IntegerField(default=5, verbose_name="Severidad (1-10)")
    descripcion = models.TextField(verbose_name="Descripción")
    datos = models.JSONField(default=dict, verbose_name="Datos del evento")
    resuelto = models.BooleanField(default=False, verbose_name="¿Resuelto?")
    fecha_evento = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha del evento"
    )

    class Meta:
        db_table = "evento"
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-severidad", "-fecha_evento"]

    def __str__(self):
        estado = "✓" if self.resuelto else "⚠"
        return f"{estado} {self.get_tipo_display()} - Sev.{self.severidad}"


class DatoEntrenamiento(models.Model):
    """Datos recolectados para entrenamiento de IA"""

    fuente_url = models.URLField(blank=True, verbose_name="URL de origen")
    consulta = models.TextField(verbose_name="Consulta")
    contenido_raw = models.TextField(verbose_name="Contenido crudo")
    features = models.JSONField(default=dict, verbose_name="Features extraídas")
    categoria_equipo = models.IntegerField(
        choices=CategoriaEquipo.choices, null=True, blank=True
    )
    prioridad = models.IntegerField(choices=Prioridad.choices, null=True, blank=True)
    usado_entrenamiento = models.BooleanField(default=False)
    conjunto = models.CharField(max_length=20, blank=True)  # train/val/test
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dato_entrenamiento"
        verbose_name = "Dato de Entrenamiento"
        verbose_name_plural = "Datos de Entrenamiento"
        ordering = ["-fecha_creacion"]


class ModeloIA(models.Model):
    """Estado y configuración del modelo de IA"""

    nombre = models.CharField(max_length=100, verbose_name="Nombre del modelo")
    version = models.CharField(max_length=20, verbose_name="Versión")

    # Configuración
    hiperparametros = models.JSONField(default=dict, verbose_name="Hiperparámetros")

    # Estado actual
    estado = models.CharField(max_length=20, default="idle", verbose_name="Estado")
    precision_actual = models.FloatField(default=0.0, verbose_name="Precisión actual")
    datos_entrenamiento = models.IntegerField(
        default=0, verbose_name="Datos de entrenamiento"
    )
    epocas_completadas = models.IntegerField(
        default=0, verbose_name="Épocas completadas"
    )

    # Historial
    historial_metricas = models.JSONField(
        default=list, verbose_name="Historial de métricas"
    )
    fecha_ultimo_entrenamiento = models.DateTimeField(null=True, blank=True)

    # Modelo serializado
    modelo_path = models.CharField(
        max_length=500, blank=True, verbose_name="Path del modelo"
    )

    activo = models.BooleanField(default=True, verbose_name="¿Activo?")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "modelo_ia"
        verbose_name = "Modelo de IA"
        verbose_name_plural = "Modelos de IA"
        ordering = ["-activo", "-fecha_creacion"]

    def __str__(self):
        return f"{self.nombre} v{self.version} ({self.precision_actual:.2%})"
