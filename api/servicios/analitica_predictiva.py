import random
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, F
from api.models import Equipo, Mantenimiento


class AnaliticaPredictiva:
    @staticmethod
    def analizar_riesgo_equipos():
        """
        Analiza todos los equipos y determina el riesgo de falla
        basado en sus mantenimientos históricos (MTBF).
        """
        resultados = []
        equipos = Equipo.objects.all()

        for eq in equipos:
            # 1. Calcular MTBF (Tiempo medio entre fallas/mantenimientos)
            mants = Mantenimiento.objects.filter(
                equipo=eq,
                estado=4,  # Falta Mantenimiento.ESTADO_COMPLETADO si no importo la flag, uso 4
                fecha_completada__isnull=False,
            ).order_by("fecha_completada")

            riesgo = "Bajo"
            score = 0.0
            dias_prox_falla = None
            mtbf = 0

            if mants.count() >= 2:
                # Calcular diferencias entre mantenimientos
                fechas = [m.fecha_completada for m in mants]
                diferencias = [
                    (fechas[i + 1] - fechas[i]).days for i in range(len(fechas) - 1)
                ]
                if diferencias:
                    mtbf = sum(diferencias) / len(diferencias)

                    # Último mantenimiento
                    ultimo_mant = fechas[-1]
                    dias_desde_ultimo = (timezone.now() - ultimo_mant).days

                    # Proyección
                    dias_restantes = max(0, mtbf - dias_desde_ultimo)
                    dias_prox_falla = int(dias_restantes)

                    # Determinar Riesgo
                    if dias_restantes < 7:
                        riesgo = "Crítico"
                        score = 0.95
                    elif dias_restantes < 30:
                        riesgo = "Alto"
                        score = 0.7
                    elif dias_restantes < 60:
                        riesgo = "Medio"
                        score = 0.4

            # Si es equipo muy viejo también sube riesgo (fallback si no hay history)
            elif (timezone.now().date() - eq.fecha_instalacion).days > 365 * 5:
                riesgo = "Medio"
                score = 0.5
                dias_prox_falla = 30  # Estimado genérico

            if riesgo in ["Crítico", "Alto", "Medio"]:
                resultados.append(
                    {
                        "equipo_id": eq.id,
                        "nombre": eq.nombre,
                        "categoria": (
                            eq.get_categoria_display()
                            if hasattr(eq, "get_categoria_display")
                            else eq.categoria
                        ),
                        "mtbf_dias": int(mtbf),
                        "dias_prox_falla": (
                            dias_prox_falla
                            if dias_prox_falla is not None
                            else "Desconocido"
                        ),
                        "riesgo": riesgo,
                        "score": score,
                    }
                )

        # Ordenar por urgencia (score descendente)
        return sorted(resultados, key=lambda x: x["score"], reverse=True)
