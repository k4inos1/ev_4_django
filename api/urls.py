from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from .views import (
    EquipoViewSet,
    MantenimientoViewSet,
    RecursoViewSet,
    EventoViewSet,
    DatabaseExplorerViewSet,
    IADashboardViewSet,
)
from .views_sistema import SistemaInteligenteViewSet

# Router para endpoints de la API
router = DefaultRouter()

# Endpoints principales (CRUD)
router.register(r"equipos", EquipoViewSet, basename="equipo")
router.register(r"mantenimientos", MantenimientoViewSet, basename="mantenimiento")
router.register(r"recursos", RecursoViewSet, basename="recurso")
router.register(r"eventos", EventoViewSet, basename="evento")

# Dashboard
router.register(r"db", DatabaseExplorerViewSet, basename="db-explorer")

# Dashboard IA
from .views_dashboard import IADashboardViewSet

router.register(r"ia-dashboard", IADashboardViewSet, basename="ia-dashboard")

# Sistema Inteligente (Principal)
router.register(r"sistema", SistemaInteligenteViewSet, basename="sistema-inteligente")

# Analytics y Consultas
from .views_analytics import AnalyticsViewSet

router.register(r"analytics", AnalyticsViewSet, basename="analytics")

urlpatterns = [
    # API versionada
    path("v1/", include("api.v1.urls")),
    path("v2/", include("api.v2.urls")),
    # API sin versión (redirect a v1)
    path("", include(router.urls)),
    # Documentacion
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
