from django.utils import timezone
from api.models import Equipo, Mantenimiento, Recurso
from api.servicios.analitica_predictiva import AnaliticaPredictiva
from api.servicios.optimizador_inventario import OptimizadorInventario


class ChatService:
    @staticmethod
    def procesar_mensaje(mensaje):
        msg = mensaje.lower()
        respuesta = "Lo siento, no entendí tu consulta. Intenta preguntar por 'estado de [equipo]', 'riesgos' o 'inventario'."

        # Intención: Consultar Estado de Equipo
        if "estado" in msg or "información" in msg or "info" in msg:
            equipos = Equipo.objects.all()
            encontrado = None
            for eq in equipos:
                if eq.nombre.lower() in msg:
                    encontrado = eq
                    break

            if encontrado:
                mants_pend = Mantenimiento.objects.filter(
                    equipo=encontrado, estado=1
                ).count()
                respuesta = f"🤖 **{encontrado.nombre}** ({encontrado.get_categoria_display()}):\n"
                respuesta += (
                    f"- Estado: {'🔴 Crítico' if mants_pend > 0 else '🟢 Operativo'}\n"
                )
                respuesta += f"- Pendientes: {mants_pend} mantenimientos.\n"
                respuesta += f"- Ubicación: {encontrado.ubicacion}"
            elif "estado" in msg:
                respuesta = (
                    "No encontré ese equipo. ¿Podrías especificar el nombre exacto?"
                )

        # Intención: Consultar Riesgos / Predicciones
        elif "riesgo" in msg or "falla" in msg or "peligro" in msg:
            riesgos = AnaliticaPredictiva.analizar_riesgo_equipos()
            criticos = [r for r in riesgos if r["riesgo"] in ["Crítico", "Alto"]]

            if criticos:
                respuesta = f"⚠️ He detectado **{len(criticos)} equipos en riesgo**:\n"
                for c in criticos[:3]:
                    respuesta += f"- **{c['nombre']}**: {c['riesgo']} (Falla en ~{c['dias_prox_falla']} días)\n"
                if len(criticos) > 3:
                    respuesta += f"... y {len(criticos)-3} más."
            else:
                respuesta = "✅ No detecto riesgos inminentes en la planta. Todo parece bajo control."

        # Intención: Consultar Inventario / Repuestos
        elif (
            "stock" in msg
            or "inventario" in msg
            or "repuestos" in msg
            or "falta" in msg
        ):
            analisis = OptimizadorInventario.analizar_stock()
            bajos = [s for s in analisis if s["estado"] != "OK"]

            if bajos:
                respuesta = f"📦 Informe de Inventario:\n"
                for b in bajos[:3]:
                    respuesta += f"- **{b['nombre']}**: Quedan {b['stock_actual']} (Sugerido comprar {b['cantidad_sugerida']})\n"
            else:
                respuesta = "✅ El inventario está saludable."

        # Intención: Ejecutar Acciones
        elif "ejecuta" in msg or "accionar" in msg or "mantenimiento" in msg:
            if "automata" in msg or "ahora" in msg:
                from api.servicios.automata import AutomataInteligente

                res = AutomataInteligente.ejecutar_ciclo_autonomo()
                respuesta = f"⚙️ **Autómata Ejecutado**:\n- Acciones: {res['total_acciones']}\n- Riesgos cubiertos: {res['riesgos_detectados']}"

        # Saludo
        elif "hola" in msg or "buenos días" in msg:
            respuesta = (
                "👋 ¡Hola! Soy el asistente IA de EV4. ¿En qué puedo ayudarte hoy?"
            )

        return respuesta
