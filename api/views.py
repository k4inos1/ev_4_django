from rest_framework import viewsets
from .models import Emp, Eq, Tec, PM, OT
from .serializers import (
    SerEmp,
    SerEq,
    SerTec,
    SerPM,
    SerOT,
)

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from .services import ServIA, ServOT, ServGral  # Modern Service Layer


class PagN(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class VSBase(viewsets.ModelViewSet):
    f_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = PagN

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "s_query"):
            self.queryset = self.s_query
        if hasattr(self, "s_class"):
            self.serializer_class = self.s_class
        if hasattr(self, "c_fil"):
            self.filterset_fields = self.c_fil
        if hasattr(self, "c_bus"):
            self.search_fields = self.c_bus
        if hasattr(self, "c_ord"):
            self.ordering_fields = self.c_ord
        if hasattr(self, "f_backends"):
            self.filter_backends = self.f_backends


class EmpVS(VSBase):
    s_query = Emp.objects.all()
    s_class = SerEmp
    c_fil = ["rut"]
    c_bus = ["nombre", "direccion"]
    c_ord = ["nombre", "created_at"]


class EqVS(VSBase):
    s_query = Eq.objects.select_related("empresa").all()
    s_class = SerEq
    c_fil = ["empresa", "critico"]
    c_bus = ["nombre", "serie"]
    c_ord = ["fecha_instalacion"]


class TecVS(VSBase):
    s_query = Tec.objects.select_related("usuario").all()
    s_class = SerTec
    c_fil = ["especialidad"]
    c_bus = ["nombre"]
    c_ord = ["nombre"]


class PMVS(VSBase):
    s_query = PM.objects.select_related("equipo").all()
    s_class = SerPM
    c_fil = ["activo", "equipo"]
    c_bus = ["nombre"]
    c_ord = ["frecuencia"]


class OTVS(VSBase):
    s_query = OT.objects.select_related("plan", "equipo", "tecnico").all()
    s_class = SerOT
    c_fil = ["estado", "tecnico", "equipo"]
    c_bus = ["notas"]
    c_ord = ["fecha_programada", "estado"]

    @action(detail=True, methods=["post"])
    def analizar(self, request, pk=None):
        """
        Endpoint IA (Usa ServIA).
        """
        ot = self.get_object()

        # 1. Calc P
        p_a = ServIA.calc_p(ot.notas)

        # 2. Busc T
        cat = ot.equipo.categoria
        rec = ServIA.busc_t(cat)

        return Response(
            {
                "act_p": ot.prioridad,
                "cal_p": p_a,
                "match": {"eq": ot.equipo.nombre, "cat": cat, "rec": rec},
            }
        )


class ResumenVS(viewsets.ViewSet):
    """
    Vista de Resumen Global (Datos Totales).
    """

    def list(self, request):
        """
        Devuelve el payload de Servicio General.
        """
        data = ServGral.resumen_api()
        return Response(data)
