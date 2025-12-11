from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from api.servicios.ia_core import ia_sistema
from api.models import Mantenimiento, Recurso


@extend_schema(tags=["Sistema Inteligente"])
class SistemaInteligenteViewSet(viewsets.ViewSet):
    """
    API del sistema inteligente

    Combina: IA + RL + Web Scraping + Automatizacion
    """

    permission_classes = []

    @extend_schema(
        summary="Tomar decision inteligente",
        description="Usa IA + RL para tomar la mejor decision",
    )
    @action(detail=False, methods=["post"])
    def decidir(self, request):
        """
        Toma una decision inteligente

        Body:
        {
            "tipo": "prioridad" | "tecnico",
            "descripcion": "Texto descriptivo",
            "contexto": {
                "categoria": 1,
                "tipo": "preventivo",
                "prioridad": 100
            },
            "mantenimiento_id": 123  // Para decision de tecnico
        }
        """
        tipo = request.data.get("tipo")
        descripcion = request.data.get("descripcion", "")
        contexto = request.data.get("contexto", {})

        if tipo == "prioridad":
            # Decidir prioridad
            prioridad = ia_sistema.decidir_prioridad(descripcion, contexto)

            return Response(
                {
                    "tipo": "prioridad",
                    "decision": prioridad,
                    "descripcion": descripcion,
                    "metodo": "IA + RL",
                    "rust_usado": ia_sistema.obtener_estadisticas()["rust_habilitado"],
                }
            )

        elif tipo == "tecnico":
            # Decidir tecnico
            mantenimiento_id = request.data.get("mantenimiento_id")

            if not mantenimiento_id:
                return Response(
                    {"error": "mantenimiento_id requerido para decision de tecnico"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                mantenimiento = Mantenimiento.objects.get(id=mantenimiento_id)
                tecnicos = Recurso.objects.filter(
                    tipo=Recurso.TIPO_TECNICO, disponible=True
                )

                decision = ia_sistema.decidir_tecnico(mantenimiento, list(tecnicos))

                if decision:
                    return Response(
                        {
                            "tipo": "tecnico",
                            "decision": {
                                "tecnico_id": decision["tecnico"].id,
                                "tecnico_nombre": decision["tecnico"].nombre,
                                "especialidad": decision["tecnico"].especialidad,
                                "calificacion": decision["tecnico"].calificacion,
                                "confianza": decision["confianza"],
                            },
                            "metodo": "RL basado en experiencia",
                        }
                    )
                else:
                    return Response(
                        {"error": "No hay tecnicos disponibles"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

            except Mantenimiento.DoesNotExist:
                return Response(
                    {"error": "Mantenimiento no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {"error": f'Tipo de decision "{tipo}" no soportado'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Registrar aprendizaje",
        description="Aprende de un resultado para mejorar futuras decisiones",
    )
    @action(detail=False, methods=["post"])
    def aprender(self, request):
        """
        Aprende de un resultado

        Body:
        {
            "mantenimiento_id": 123,
            "resultado": {
                "fue_exitoso": true,
                "dias_resolucion": 5,
                "costo_esperado": 1000,
                "costo_real": 800
            }
        }
        """
        mantenimiento_id = request.data.get("mantenimiento_id")
        resultado = request.data.get("resultado", {})

        if not mantenimiento_id:
            return Response(
                {"error": "mantenimiento_id requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            mantenimiento = Mantenimiento.objects.get(id=mantenimiento_id)

            # Aprender del resultado
            aprendizaje = ia_sistema.aprender_de_resultado(mantenimiento, resultado)

            return Response(
                {
                    "mensaje": "Sistema aprendio de la experiencia",
                    "aprendizaje": aprendizaje,
                    "precision_sistema": aprendizaje["precision_sistema"],
                }
            )

        except Mantenimiento.DoesNotExist:
            return Response(
                {"error": "Mantenimiento no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        summary="Aprender de la web",
        description="Busca informacion en internet y aprende automaticamente",
    )
    @action(detail=False, methods=["post"])
    def aprender_web(self, request):
        """
        Aprende de busquedas web

        Body:
        {
            "tema": "industrial maintenance procedures",
            "max_resultados": 5
        }
        """
        tema = request.data.get("tema")
        max_resultados = request.data.get("max_resultados", 5)

        if not tema:
            return Response(
                {"error": "Tema de busqueda requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Aprender de web
        resultado = ia_sistema.aprender_de_web(tema, max_resultados)

        return Response(
            {"mensaje": "Sistema aprendio de la web", "resultado": resultado}
        )

    @extend_schema(
        summary="Estadisticas del sistema",
        description="Obtiene estadisticas completas del sistema inteligente",
    )
    @action(detail=False, methods=["get"])
    def estadisticas(self, request):
        """Estadisticas completas"""
        stats = ia_sistema.obtener_estadisticas()

        return Response(
            {
                "sistema": "IA Sistema",
                "version": "2.0",
                "estadisticas": stats,
                "capacidades": [
                    "Decisiones de prioridad (IA + RL)",
                    "Asignacion de tecnicos (RL)",
                    "Aprendizaje de resultados",
                    "Aprendizaje de web scraping",
                    "Optimizacion continua",
                ],
            }
        )

    @extend_schema(
        summary="Reiniciar conocimiento",
        description="Reinicia el conocimiento del sistema (usar con precaucion)",
    )
    @action(detail=False, methods=["post"])
    def reiniciar(self, request):
        """Reinicia el conocimiento"""
        resultado = ia_sistema.reiniciar_conocimiento()

        return Response({"mensaje": "Conocimiento reiniciado", "resultado": resultado})

    @extend_schema(
        summary="Exportar conocimiento",
        description="Exporta todo el conocimiento del sistema",
    )
    @action(detail=False, methods=["get"])
    def exportar(self, request):
        """Exporta conocimiento completo"""
        stats = ia_sistema.obtener_estadisticas()

        return Response(
            {
                "q_table": ia_sistema.q_table,
                "metricas": ia_sistema.metricas,
                "configuracion": stats["configuracion"],
                "total_conocimiento": {
                    "estados": stats["total_estados"],
                    "acciones": stats["total_acciones"],
                },
            }
        )

    # ========================================
    # AUTOMATIZACION (BOTONES DASHBOARD)
    # ========================================

    @extend_schema(
        summary="Generar datos automaticamente",
        description="Genera datos sinteticos via comando (boton dashboard)",
    )
    @action(detail=False, methods=["post"])
    def generar_datos(self, request):
        """
        Genera datos automaticamente

        Body: {"cantidad": 50}
        """
        from django.core.management import call_command
        from io import StringIO
        import sys

        cantidad = request.data.get("cantidad", 50)

        try:
            output = StringIO()
            sys.stdout = output
            call_command("generar_datos", cantidad=cantidad)
            sys.stdout = sys.__stdout__

            from api.models import Equipo, Mantenimiento

            return Response(
                {
                    "mensaje": f"{cantidad} registros generados exitosamente",
                    "cantidad": cantidad,
                    "totales": {
                        "equipos": Equipo.objects.count(),
                        "mantenimientos": Mantenimiento.objects.count(),
                    },
                }
            )
        except Exception as e:
            sys.stdout = sys.__stdout__
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Pipeline automatico completo",
        description="Web scraping + generacion + entrenamiento (boton dashboard)",
    )
    @action(detail=False, methods=["post"])
    def pipeline_auto(self, request):
        """
        Pipeline completo: scraping + datos + IA

        Body: {
            "busquedas": 5,
            "generar": 30,
            "entrenar": true
        }
        """
        from django.core.management import call_command
        from io import StringIO
        import sys

        busquedas = request.data.get("busquedas", 5)
        generar = request.data.get("generar", 30)
        entrenar = request.data.get("entrenar", True)

        resultados = []

        try:
            # Web scraping + generacion
            output = StringIO()
            sys.stdout = output
            call_command("aprender_web", busquedas=busquedas, generar=generar)
            sys.stdout = sys.__stdout__
            resultados.append(f"Web scraping: {busquedas} busquedas")
            resultados.append(f"Datos generados: {generar}")

            # Entrenar IA
            if entrenar:
                from api.servicios import ServicioIA

                ServicioIA.iniciar_entrenamiento(epochs=5, n_samples=50)
                resultados.append("IA entrenada")

            from api.models import Equipo, Mantenimiento

            return Response(
                {
                    "mensaje": "Pipeline completado exitosamente",
                    "pasos": resultados,
                    "totales": {
                        "equipos": Equipo.objects.count(),
                        "mantenimientos": Mantenimiento.objects.count(),
                    },
                }
            )

        except Exception as e:
            sys.stdout = sys.__stdout__
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
