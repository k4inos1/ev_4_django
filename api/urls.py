from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EmpVS,
    EqVS,
    TecVS,
    PMVS,
    OTVS,
    ResumenVS,
)

ruteador = DefaultRouter()
ruteador.register(r"emp", EmpVS, basename="emp")
ruteador.register(r"eq", EqVS, basename="eq")
ruteador.register(r"tec", TecVS, basename="tec")
ruteador.register(r"pm", PMVS, basename="pm")
ruteador.register(r"ot", OTVS, basename="ot")
ruteador.register(r"resumen", ResumenVS, basename="resumen")

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularJSONView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path("api/", include(ruteador.urls)),
    # Documentacion
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/json/", SpectacularJSONView.as_view(), name="schema-json"),
    path(
        "schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema-json"),
        name="swagger-ui",
    ),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema-json"),
        name="redoc",
    ),
]
