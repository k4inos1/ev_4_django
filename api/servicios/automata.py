from django.utils import timezone
from api.models import Equipo, Mantenimiento, Evento, Recurso
from api.servicios.analitica_predictiva import AnaliticaPredictiva
from api.servicios.optimizador_inventario import OptimizadorInventario


class AutomataInteligente:
    @staticmethod
    def ejecutar_ciclo_autonomo():
        """
        Ejecuta acciones correctivas automáticamente basado en predicciones.
        """
        acciones_tomadas = []

        # 1. Análisis de Riesgos (Equipos)
        analisis_equipos = AnaliticaPredictiva.analizar_riesgo_equipos()
        equipos_criticos = [e for e in analisis_equipos if e["riesgo"] == "Crítico"]

        for eq_data in equipos_criticos:
            # Verificar si ya existe un mantenimiento pendiente para no duplicar
            existe_pendiente = Mantenimiento.objects.filter(
                equipo_id=eq_data["equipo_id"], estado=1  # Pendiente
            ).exists()

            if not existe_pendiente:
                # CREAR MANTENIMIENTO AUTOMÁTICO
                nuevo_mant = Mantenimiento.objects.create(
                    equipo_id=eq_data["equipo_id"],
                    fecha_programada=timezone.now() + timezone.timedelta(days=1),
                    tipo="Preventivo",
                    prioridad=10,  # Máxima prioridad
                    descripcion=f"AUTO: Mantenimiento Preventivo generado por IA. Riesgo detectado: {eq_data['riesgo']}. MTBF excedido.",
                    estado=1,  # Pendiente
                )
                acciones_tomadas.append(
                    f"Mantenimiento creado para equipo {eq_data['nombre']} (ID: {nuevo_mant.id})"
                )

        # 2. Análisis de Stock (Recursos)
        analisis_stock = OptimizadorInventario.analizar_stock()
        stock_critico = [s for s in analisis_stock if s["estado"] == "Crítico"]

        for st_data in stock_critico:
            # Registrar Evento de Solicitud de Compra
            evento = Evento.objects.create(
                tipo="Sistema",
                severidad=5,  # Media
                descripcion=f"AUTO: Solicitud de compra para {st_data['nombre']}. Stock: {st_data['stock_actual']}. Sugerido: +{st_data['cantidad_sugerida']}.",
                resuelto=False,
            )
            acciones_tomadas.append(
                f"Alerta de compra generada para recurso {st_data['nombre']}"
            )

        return {
            "total_acciones": len(acciones_tomadas),
            "detalle": acciones_tomadas,
            "riesgos_detectados": len(equipos_criticos),
            "alertas_stock": len(stock_critico),
        }
