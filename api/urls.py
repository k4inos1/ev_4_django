from django.urls import include, path
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

# Endpoints principales
router.register(r"equipos", EquipoViewSet, basename="equipo")
router.register(r"mantenimientos", MantenimientoViewSet, basename="mantenimiento")
router.register(r"recursos", RecursoViewSet, basename="recurso")
router.register(r"eventos", EventoViewSet, basename="evento")

# Dashboard endpoints
router.register(r"db", DatabaseExplorerViewSet, basename="db-explorer")
router.register(r"ia-dashboard", IADashboardViewSet, basename="ia-dashboard")

# IA endpoints (legacy - mantener compatibilidad)
router.register(r"ia/datos", DatoEntrenamientoViewSet, basename="dato-entrenamiento")
router.register(
    r"ia/entrenamiento", EntrenamientoIAViewSet, basename="entrenamiento-ia"
)

# RL endpoints (legacy)
router.register(r"rl", ReinforcementLearningViewSet, basename="reinforcement-learning")

# Sistema Inteligente Unificado (NUEVO - recomendado)
router.register(
    r"inteligente", SistemaInteligenteViewSet, basename="sistema-inteligente"
)

urlpatterns = [
    # API endpoints
    path("", include(router.urls)),
    # Documentación con ReDoc
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularRedocView.as_view(url_name="schema"), name="api-docs"),
]
