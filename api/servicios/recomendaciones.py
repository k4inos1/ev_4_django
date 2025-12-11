"""
Motor de Recomendaciones Proactivas
"""

from datetime import datetime, timedelta
from django.db.models import Avg, Count, Q
from api.models import Equipo, Mantenimiento, Recomendacion, BaseConocimiento


class MotorRecomendaciones:
    """Sistema de recomendaciones proactivas basado en IA"""

    @staticmethod
    def generar_recomendaciones_equipo(equipo_id):
        """Genera recomendaciones para un equipo específico"""
        try:
            equipo = Equipo.objects.get(id=equipo_id)
            recomendaciones = []

            # 1. Predecir próximo mantenimiento
            rec_mantenimiento = MotorRecomendaciones._predecir_mantenimiento(equipo)
            if rec_mantenimiento:
                recomendaciones.append(rec_mantenimiento)

            # 2. Alertas de criticidad
            if equipo.es_critico:
                rec_alerta = MotorRecomendaciones._generar_alerta_critica(equipo)
                if rec_alerta:
                    recomendaciones.append(rec_alerta)

            # 3. Optimización de costos
            rec_costo = MotorRecomendaciones._optimizar_costos(equipo)
            if rec_costo:
                recomendaciones.append(rec_costo)

            return recomendaciones

        except Equipo.DoesNotExist:
            return []

    @staticmethod
    def _predecir_mantenimiento(equipo):
        """Predice cuándo necesitará mantenimiento"""
        # Obtener historial
        mantenimientos = Mantenimiento.objects.filter(
            equipo=equipo, estado=4, fecha_completada__isnull=False  # 4 = completado
        ).order_by("-fecha_completada")[:5]

        if mantenimientos.count() < 2:
            return None

        # Calcular promedio de días entre mantenimientos
        intervalos = []
        for i in range(len(mantenimientos) - 1):
            delta = (
                mantenimientos[i].fecha_completada
                - mantenimientos[i + 1].fecha_completada
            ).days
            intervalos.append(delta)

        if not intervalos:
            return None

        promedio_dias = sum(intervalos) / len(intervalos)
        ultimo = mantenimientos[0]
        dias_desde_ultimo = (
            datetime.now().date() - ultimo.fecha_completada.date()
        ).days

        # Si está cerca del promedio, recomendar
        if dias_desde_ultimo >= promedio_dias * 0.8:
            confianza = min(dias_desde_ultimo / promedio_dias, 1.0)
            from django.utils import timezone

            return Recomendacion.objects.create(
                equipo=equipo,
                tipo=Recomendacion.TIPO_MANTENIMIENTO,
                prioridad=(
                    Recomendacion.PRIORIDAD_ALTA
                    if confianza > 0.9
                    else Recomendacion.PRIORIDAD_MEDIA
                ),
                titulo=f"Mantenimiento preventivo recomendado",
                descripcion=f"Basado en historial, este equipo necesitará mantenimiento en ~{int(promedio_dias - dias_desde_ultimo)} días",
                accion_sugerida="Programar mantenimiento preventivo",
                confianza=confianza,
                fecha_estimada=timezone.now()
                + timedelta(days=int(promedio_dias - dias_desde_ultimo)),
            )

        return None

    @staticmethod
    def _generar_alerta_critica(equipo):
        """Genera alerta para equipos críticos"""
        # Verificar si tiene mantenimientos pendientes
        pendientes = Mantenimiento.objects.filter(
            equipo=equipo, estado=1  # 1 = pendiente (ESTADO_PENDIENTE)
        ).count()

        if pendientes > 2:
            return Recomendacion.objects.create(
                equipo=equipo,
                tipo=Recomendacion.TIPO_ALERTA,
                prioridad=Recomendacion.PRIORIDAD_CRITICA,
                titulo="Equipo crítico con múltiples tareas pendientes",
                descripcion=f"Este equipo crítico tiene {pendientes} mantenimientos pendientes",
                accion_sugerida="Priorizar y asignar recursos inmediatamente",
                confianza=1.0,
            )

        return None

    @staticmethod
    def _optimizar_costos(equipo):
        """Sugiere optimización de costos"""
        # Analizar costos históricos
        mantenimientos = Mantenimiento.objects.filter(
            equipo=equipo, costo__isnull=False
        )

        if mantenimientos.count() < 3:
            return None

        costo_promedio = mantenimientos.aggregate(Avg("costo"))["costo__avg"]
        ultimo_costo = mantenimientos.order_by("-fecha_completada").first().costo

        if ultimo_costo and ultimo_costo > costo_promedio * 1.3:
            ahorro = ultimo_costo - costo_promedio

            return Recomendacion.objects.create(
                equipo=equipo,
                tipo=Recomendacion.TIPO_COSTO,
                prioridad=Recomendacion.PRIORIDAD_MEDIA,
                titulo="Oportunidad de optimización de costos",
                descripcion=f"Último mantenimiento costó ${ultimo_costo}, 30% más que el promedio (${costo_promedio:.2f})",
                accion_sugerida="Revisar proveedores o técnicos asignados",
                confianza=0.75,
                ahorro_estimado=ahorro,
            )

        return None

    @staticmethod
    def generar_todas_recomendaciones():
        """Genera recomendaciones para todos los equipos"""
        equipos = Equipo.objects.all()
        total = 0

        for equipo in equipos:
            recs = MotorRecomendaciones.generar_recomendaciones_equipo(equipo.id)
            total += len(recs)

        return total


# Instancia global
motor_recomendaciones = MotorRecomendaciones()
