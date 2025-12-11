"""
Vista del Dashboard IA
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg
from api.models import Equipo, Mantenimiento, AprendizajeAutomatico, Recomendacion


class IADashboardViewSet(viewsets.ViewSet):
    """Dashboard de IA"""

    @action(detail=False, methods=["get"])
    def estadisticas(self, request):
        """Estadísticas para el dashboard"""
        return Response(
            {
                "equipos": Equipo.objects.count(),
                "mantenimientos": Mantenimiento.objects.count(),
                "precision": AprendizajeAutomatico.objects.aggregate(
                    avg_precision=Avg("precision_prediccion")
                )["avg_precision"]
                or 0,
                "recomendaciones": Recomendacion.objects.filter(vista=False).count(),
            }
        )
