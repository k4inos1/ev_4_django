"""
API v2 - Features avanzadas
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from api.views import (
    EquipoViewSet,
    MantenimientoViewSet,
    RecursoViewSet,
    EventoViewSet,
)
from api.views_sistema import SistemaInteligenteViewSet


@api_view(["GET"])
@permission_classes([AllowAny])
def recomendaciones_list(request):
    """Lista de recomendaciones (v2)"""
    from api.models import Recomendacion
    from api.serializers import RecomendacionSerializer

    recomendaciones = Recomendacion.objects.filter(vista=False)[:10]
    serializer = RecomendacionSerializer(recomendaciones, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def generar_recomendaciones(request):
    """Generar recomendaciones automáticamente"""
    from api.servicios.recomendaciones import motor_recomendaciones

    total = motor_recomendaciones.generar_todas_recomendaciones()
    return Response({"mensaje": f"{total} recomendaciones generadas", "total": total})


router = DefaultRouter()
router.register(r"equipos", EquipoViewSet, basename="equipo-v2")
router.register(r"mantenimientos", MantenimientoViewSet, basename="mantenimiento-v2")
router.register(r"recursos", RecursoViewSet, basename="recurso-v2")
router.register(r"eventos", EventoViewSet, basename="evento-v2")
router.register(r"sistema", SistemaInteligenteViewSet, basename="sistema-v2")

urlpatterns = [
    path("", include(router.urls)),
    path("recomendaciones/", recomendaciones_list, name="recomendaciones-list"),
    path(
        "recomendaciones/generar/",
        generar_recomendaciones,
        name="recomendaciones-generar",
    ),
]
