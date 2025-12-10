from rest_framework import viewsets
from .models import Company, Equipment, Technician, MaintenancePlan, WorkOrder
from .serializers import (
    CompanySerializer,
    EquipmentSerializer,
    TechnicianSerializer,
    MaintenancePlanSerializer,
    WorkOrderSerializer,
)

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination


class NPaginacion(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class BaseViewSet(viewsets.ModelViewSet):
    f_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = NPaginacion

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "s_query"):
            self.queryset = self.s_query
        if hasattr(self, "s_class"):
            self.serializer_class = self.s_class
        if hasattr(self, "fs_fields"):
            self.filterset_fields = self.fs_fields
        if hasattr(self, "s_fields"):
            self.search_fields = self.s_fields
        if hasattr(self, "o_fields"):
            self.ordering_fields = self.o_fields
        if hasattr(self, "f_backends"):
            self.filter_backends = self.f_backends


class CompanyViewSet(BaseViewSet):
    s_query = Company.objects.all()
    s_class = CompanySerializer
    fs_fields = ["rut"]
    s_fields = ["nombre", "direccion"]
    o_fields = ["nombre", "created_at"]


class EquipmentViewSet(BaseViewSet):
    s_query = Equipment.objects.select_related("empresa").all()
    s_class = EquipmentSerializer
    fs_fields = ["empresa", "critico"]
    s_fields = ["nombre", "serie"]
    o_fields = ["fecha_instalacion"]


class TechnicianViewSet(BaseViewSet):
    s_query = Technician.objects.select_related("usuario").all()
    s_class = TechnicianSerializer
    fs_fields = ["especialidad"]
    s_fields = ["nombre"]
    o_fields = ["nombre"]


class MaintenancePlanViewSet(BaseViewSet):
    s_query = MaintenancePlan.objects.select_related("equipo").all()
    s_class = MaintenancePlanSerializer
    fs_fields = ["activo", "equipo"]
    s_fields = ["nombre"]
    o_fields = ["frecuencia"]


from rest_framework.decorators import action
from rest_framework.response import Response
from .ai_service import AIService


class WorkOrderViewSet(BaseViewSet):
    s_query = WorkOrder.objects.select_related("plan", "equipo", "tecnico").all()
    s_class = WorkOrderSerializer
    fs_fields = ["estado", "tecnico", "equipo"]
    s_fields = ["notas"]
    o_fields = ["fecha_programada", "estado"]

    @action(detail=True, methods=["post"])
    def analyze(self, request, pk=None):
        """
        AI Endpoint to analyze a specific Work Order.
        Returns suggested priority and recommended technician.
        """
        work_order = self.get_object()

        # 1. AI Analysis for Priority
        suggested_priority = AIService.analyze_priority(work_order.notas)

        # 2. AI Recommendation for Technician
        # Use the category of the equipment associated with the order
        equipment_category = work_order.equipo.categoria
        recommendation = AIService.recommend_technician(equipment_category)

        return Response(
            {
                "current_priority": work_order.prioridad,
                "suggested_priority": suggested_priority,
                "match_analysis": {
                    "equipment": work_order.equipo.nombre,
                    "category": equipment_category,
                    "recommended_technician": recommendation,
                },
            }
        )
