"""
API v1 - Versión estable
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    EquipoViewSet,
    MantenimientoViewSet,
    RecursoViewSet,
    EventoViewSet,
)
from api.views_sistema import SistemaInteligenteViewSet

router = DefaultRouter()
router.register(r"equipos", EquipoViewSet, basename="equipo")
router.register(r"mantenimientos", MantenimientoViewSet, basename="mantenimiento")
router.register(r"recursos", RecursoViewSet, basename="recurso")
router.register(r"eventos", EventoViewSet, basename="evento")
router.register(r"sistema", SistemaInteligenteViewSet, basename="sistema")

urlpatterns = [
    path("", include(router.urls)),
]
