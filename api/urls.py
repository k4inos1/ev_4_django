from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CompanyViewSet,
    EquipmentViewSet,
    TechnicianViewSet,
    MaintenancePlanViewSet,
    WorkOrderViewSet,
)

router = DefaultRouter()
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"equipments", EquipmentViewSet, basename="equipment")
router.register(r"technicians", TechnicianViewSet, basename="technician")
router.register(r"plans", MaintenancePlanViewSet, basename="maintenanceplan")
router.register(r"work-orders", WorkOrderViewSet, basename="workorder")

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# from drf_spectacular.views import (
#     SpectacularAPIView,
#     SpectacularJSONView,
# )

urlpatterns = [
    path("api/", include(router.urls)),
    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Documentation
    # path("schema/", SpectacularAPIView.as_view(), name="schema"),
    # path("schema/json/", SpectacularJSONView.as_view(), name="schema-json"),
    path("schema/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
