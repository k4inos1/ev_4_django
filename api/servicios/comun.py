from api.constants import ESTADO_PENDIENTE, PRIORIDAD_ALTA
from api.models import Mantenimiento, Equipo


class ServicioMantenimiento:
    """Servicio para gestión de mantenimientos"""

    @staticmethod
    def sincronizar_prioridad(mantenimiento: Mantenimiento) -> Mantenimiento:
        """Sincroniza la prioridad de un mantenimiento usando IA"""
        from .ia import ServicioIA

        if mantenimiento.descripcion:
            prioridad = ServicioIA.calcular_prioridad(mantenimiento.descripcion)
            if prioridad != mantenimiento.prioridad:
                mantenimiento.prioridad = prioridad
        return mantenimiento


class ServicioGeneral:
    """Servicio general del sistema"""

    @staticmethod
    def obtener_pulso() -> dict:
        """Obtiene el pulso global del sistema con estadísticas"""
        from api.models import Recurso, Evento

        return {
            "global": {
                "equipos": Equipo.objects.count(),
                "mantenimientos": Mantenimiento.objects.count(),
                "recursos": Recurso.objects.count(),
                "eventos": Evento.objects.count(),
            },
            "estadisticas": {
                "mantenimientos_pendientes": Mantenimiento.objects.filter(
                    estado=ESTADO_PENDIENTE
                ).count(),
                "mantenimientos_criticos": Mantenimiento.objects.filter(
                    prioridad=PRIORIDAD_ALTA
                ).count(),
            },
            "sistema": "OK_0x1",
        }
