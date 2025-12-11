from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection
from django.apps import apps
from drf_spectacular.utils import extend_schema

from .models import Equipo, Mantenimiento, Recurso, Evento, DatoEntrenamiento, ModeloIA
from .serializers import (
    EquipoSerializer,
    MantenimientoSerializer,
    RecursoSerializer,
    EventoSerializer,
    DatoEntrenamientoSerializer,
    ModeloIASerializer,
)


class BaseViewSet(viewsets.ModelViewSet):
    """ViewSet base con configuración común"""

    permission_classes = []
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


@extend_schema(tags=["Equipos"])
class EquipoViewSet(BaseViewSet):
    """Gestión de equipos industriales"""

    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer
    search_fields = ["nombre", "empresa_nombre", "numero_serie"]
    ordering_fields = ["nombre", "es_critico", "fecha_creacion"]


@extend_schema(tags=["Mantenimiento"])
class MantenimientoViewSet(BaseViewSet):
    """Gestión de mantenimientos"""

    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer
    search_fields = ["descripcion", "tecnico_asignado"]
    ordering_fields = ["prioridad", "fecha_programada", "estado"]


@extend_schema(tags=["Recursos"])
class RecursoViewSet(BaseViewSet):
    """Gestión de recursos (técnicos, repuestos, proveedores)"""

    queryset = Recurso.objects.all()
    serializer_class = RecursoSerializer
    search_fields = ["nombre", "especialidad"]
    ordering_fields = ["tipo", "nombre", "calificacion"]


@extend_schema(tags=["Eventos"])
class EventoViewSet(BaseViewSet):
    """Gestión de eventos del sistema"""

    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    search_fields = ["descripcion"]
    ordering_fields = ["severidad", "fecha_evento", "resuelto"]


@extend_schema(tags=["Dashboard - Explorador de BD"])
class DatabaseExplorerViewSet(viewsets.ViewSet):
    """Explorador interactivo de base de datos"""

    permission_classes = []
    serializer_class = None  # ViewSet sin modelo específico

    @extend_schema(summary="Listar todas las tablas")
    @action(detail=False, methods=["get"])
    def tables(self, request):
        """Lista todas las tablas con conteo de registros"""
        tables_info = []

        for model in apps.get_app_config("api").get_models():
            tables_info.append(
                {
                    "name": model._meta.db_table,
                    "model": model.__name__,
                    "count": model.objects.count(),
                    "fields": [f.name for f in model._meta.fields],
                }
            )

        return Response({"tables": tables_info})

    @extend_schema(summary="Estadísticas generales")
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Estadísticas generales de la BD"""
        return Response(
            {
                "total_equipos": Equipo.objects.count(),
                "equipos_criticos": Equipo.objects.filter(es_critico=True).count(),
                "total_mantenimientos": Mantenimiento.objects.count(),
                "mantenimientos_pendientes": Mantenimiento.objects.filter(
                    estado=1
                ).count(),
                "total_recursos": Recurso.objects.count(),
                "recursos_disponibles": Recurso.objects.filter(disponible=True).count(),
                "total_eventos": Evento.objects.count(),
                "eventos_no_resueltos": Evento.objects.filter(resuelto=False).count(),
                "total_datos_ia": DatoEntrenamiento.objects.count(),
                "datos_ia_usados": DatoEntrenamiento.objects.filter(
                    usado_entrenamiento=True
                ).count(),
            }
        )

    @extend_schema(summary="Explorar datos de tabla")
    @action(detail=False, methods=["get"])
    def browse(self, request):
        """Obtiene datos de una tabla específica"""
        table_name = request.query_params.get("table", "equipo")
        limit = int(request.query_params.get("limit", 10))

        model_map = {
            "equipo": Equipo,
            "mantenimiento": Mantenimiento,
            "recurso": Recurso,
            "evento": Evento,
            "dato_entrenamiento": DatoEntrenamiento,
            "modelo_ia": ModeloIA,
        }

        model = model_map.get(table_name)
        if not model:
            return Response({"error": "Tabla no encontrada"}, status=400)

        # Obtener datos
        queryset = model.objects.all()[:limit]

        # Convertir a dict
        data = []
        for obj in queryset:
            item = {}
            for field in model._meta.fields:
                value = getattr(obj, field.name)
                # Convertir a string si es necesario
                if hasattr(value, "isoformat"):
                    value = value.isoformat()
                elif isinstance(value, dict) or isinstance(value, list):
                    value = str(value)
                item[field.name] = value
            data.append(item)

        return Response(
            {
                "table": table_name,
                "count": model.objects.count(),
                "data": data,
                "fields": [f.name for f in model._meta.fields],
            }
        )


@extend_schema(tags=["Dashboard - IA"])
class IADashboardViewSet(viewsets.ViewSet):
    """Dashboard de visualización de IA"""

    permission_classes = []
    serializer_class = ModeloIASerializer  # Para documentación

    @extend_schema(summary="Evolución del modelo")
    @action(detail=False, methods=["get"])
    def evolution(self, request):
        """Evolución del modelo de IA"""
        modelo = ModeloIA.objects.filter(activo=True).first()

        if not modelo:
            # Crear modelo por defecto
            modelo = ModeloIA.objects.create(
                nombre="EV4-ML-Model",
                version="1.0.0",
                hiperparametros={"epochs": 100, "learning_rate": 0.001},
            )

        return Response(
            {
                "nombre": modelo.nombre,
                "version": modelo.version,
                "precision_actual": modelo.precision_actual,
                "datos_entrenamiento": modelo.datos_entrenamiento,
                "epocas_completadas": modelo.epocas_completadas,
                "historial": modelo.historial_metricas,
                "estado": modelo.estado,
                "hiperparametros": modelo.hiperparametros,
            }
        )

    @extend_schema(summary="Pipeline de datos")
    @action(detail=False, methods=["get"])
    def data_pipeline(self, request):
        """Pipeline de datos de IA"""
        total = DatoEntrenamiento.objects.count()
        usados = DatoEntrenamiento.objects.filter(usado_entrenamiento=True).count()

        por_conjunto = {
            "train": DatoEntrenamiento.objects.filter(conjunto="train").count(),
            "val": DatoEntrenamiento.objects.filter(conjunto="val").count(),
            "test": DatoEntrenamiento.objects.filter(conjunto="test").count(),
        }

        return Response(
            {
                "total_datos": total,
                "datos_usados": usados,
                "datos_disponibles": total - usados,
                "distribucion": por_conjunto,
                "porcentaje_uso": (usados / total * 100) if total > 0 else 0,
            }
        )
