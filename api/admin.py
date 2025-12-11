from django.contrib import admin
from .models import Equipo, Mantenimiento, Recurso, Evento, DatoEntrenamiento, ModeloIA


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "empresa_nombre",
        "categoria",
        "es_critico",
        "estado",
        "numero_serie",
    ]
    list_filter = ["es_critico", "categoria", "estado"]
    search_fields = ["nombre", "empresa_nombre", "numero_serie"]
    ordering = ["-es_critico", "nombre"]


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = [
        "equipo",
        "tipo",
        "prioridad",
        "estado",
        "tecnico_asignado",
        "fecha_programada",
    ]
    list_filter = ["tipo", "prioridad", "estado"]
    search_fields = ["descripcion", "tecnico_asignado"]
    date_hierarchy = "fecha_programada"
    ordering = ["-prioridad", "fecha_programada"]


@admin.register(Recurso)
class RecursoAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "tipo",
        "disponible",
        "stock",
        "stock_minimo",
        "calificacion",
    ]
    list_filter = ["tipo", "disponible"]
    search_fields = ["nombre", "especialidad"]
    ordering = ["tipo", "nombre"]


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ["tipo", "equipo", "severidad", "resuelto", "fecha_evento"]
    list_filter = ["tipo", "resuelto", "severidad"]
    search_fields = ["descripcion"]
    date_hierarchy = "fecha_evento"
    ordering = ["-severidad", "-fecha_evento"]


@admin.register(DatoEntrenamiento)
class DatoEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ["consulta", "usado_entrenamiento", "conjunto", "fecha_creacion"]
    list_filter = ["usado_entrenamiento", "conjunto"]
    search_fields = ["consulta", "contenido_raw"]
    date_hierarchy = "fecha_creacion"


@admin.register(ModeloIA)
class ModeloIAAdmin(admin.ModelAdmin):
    list_display = [
        "nombre",
        "version",
        "estado",
        "precision_actual",
        "epocas_completadas",
        "activo",
    ]
    list_filter = ["estado", "activo"]
    search_fields = ["nombre", "version"]
    ordering = ["-activo", "-fecha_creacion"]
