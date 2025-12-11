from django.db.models import Sum, Count
from api.models import Recurso, Mantenimiento


class OptimizadorInventario:
    @staticmethod
    def analizar_stock():
        """
        Analiza el consumo de recursos y sugiere reabastecimiento inteligente.
        """
        sugerencias = []
        recursos = Recurso.objects.all()

        # Analizar consumo global (simulado o real si tuvieramos tabla intermedia RecursoMantenimiento)
        # Como en este modelo simplificado no hay ManyToMany explícito con cantidad en Mantenimiento para Recursos
        # (Recurso es un modelo independiente en esta versión simplificada, o se usa abstractamente),
        # Simularemos el análisis basado en el stock actual vs stock mínimo y tendencias.

        for r in recursos:
            # Lógica de Reorden Inteligente
            stock_actual = r.stock
            stock_min = r.stock_minimo
            consumo_estimado_mensual = max(5, int(stock_min * 1.5))  # Heurística simple

            estado = "OK"
            accion = "Ninguna"
            cantidad_sugerida = 0

            if stock_actual <= stock_min:
                estado = "Crítico"
                accion = "Comprar Urgente"
                # Sugerir comprar para cubrir 3 meses
                cantidad_sugerida = (consumo_estimado_mensual * 3) - stock_actual
            elif stock_actual < (stock_min * 1.5):
                estado = "Bajo"
                accion = "Planificar Compra"
                cantidad_sugerida = (consumo_estimado_mensual * 2) - stock_actual

            if estado != "OK":
                sugerencias.append(
                    {
                        "id": r.id,
                        "nombre": r.nombre,
                        "tipo": r.tipo,
                        "stock_actual": stock_actual,
                        "stock_minimo": stock_min,
                        "estado": estado,
                        "accion": accion,
                        "cantidad_sugerida": int(cantidad_sugerida),
                    }
                )

        return sorted(sugerencias, key=lambda x: x["stock_actual"])
