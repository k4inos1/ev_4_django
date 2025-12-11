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

    @action(detail=False, methods=["post"])
    def generar_datos_prueba(self, request):
        """Genera datos aleatorios de prueba"""
        import random
        from datetime import timedelta
        from django.utils import timezone
        from api.models import Equipo, Mantenimiento, Recurso, Evento
        from api.servicios import motor_recomendaciones

        cantidad = request.data.get("cantidad", 10)
        equipos_creados = 0
        mantenimientos_creados = 0
        recursos_creados = 0
        eventos_creados = 0
        empresas = [
            "Industrial Solutions",
            "Process Automation",
            "Manufacturing Excellence",
            "Tech Industries",
        ]

        # 1. Generar Equipos
        for i in range(cantidad):
            eq = Equipo.objects.create(
                nombre=f"Equipo-{random.randint(1000,9999)}",
                empresa_nombre=random.choice(empresas),
                categoria=random.randint(1, 5),
                numero_serie=f"SN-{random.randint(100000,999999)}",
                ubicacion=f"Planta {random.randint(1,5)} - Sector {random.choice(['A','B','C'])}",
                es_critico=random.choice([True, False]),
                estado=random.choice(["operativo", "mantenimiento", "detenido"]),
                fecha_instalacion=timezone.now()
                - timedelta(days=random.randint(30, 1000)),
            )
            equipos_creados += 1

            # 2. Generar Mantenimientos
            for j in range(random.randint(1, 3)):
                Mantenimiento.objects.create(
                    equipo=eq,
                    descripcion=f"Mantenimiento {random.choice(['preventivo','correctivo','inspección'])}",
                    tipo=random.choice(["preventivo", "correctivo", "inspeccion"]),
                    prioridad=random.randint(10, 100),
                    estado=(
                        estado_mant := random.choice([1, 2, 4])
                    ),  # Pendiente, En Progreso, Completado
                    fecha_programada=timezone.now()
                    + timedelta(days=random.randint(1, 90)),
                    fecha_completada=(
                        timezone.now() - timedelta(days=random.randint(1, 30))
                        if estado_mant == 4
                        else None
                    ),
                    tecnico_asignado=f"Técnico-{random.randint(1,10)}",
                    costo=random.uniform(100.0, 5000.0),
                )
                mantenimientos_creados += 1

            # 3. Generar Eventos (70% prob)
            if random.random() > 0.3:
                Evento.objects.create(
                    tipo=random.choice(
                        [
                            Evento.TIPO_INCIDENTE,
                            Evento.TIPO_TELEMETRIA,
                            Evento.TIPO_FLUJO,
                        ]
                    ),
                    equipo=eq,
                    severidad=random.randint(1, 10),
                    descripcion=f"Evento simulado para {eq.nombre}: {random.choice(['Alta temperatura', 'Vibración excesiva', 'Pérdida de presión', 'Voltaje inestable'])}",
                    resuelto=random.choice([True, False]),
                )
                eventos_creados += 1

            # 4. Trigger Recomendaciones
            try:
                motor_recomendaciones.generar_recomendaciones_equipo(eq.id)
            except Exception:
                pass

        # 5. Generar Recursos (Independientes)
        tipos_recurso = [
            Recurso.TIPO_REPUESTO,
            Recurso.TIPO_TECNICO,
            Recurso.TIPO_PROVEEDOR,
        ]
        for _ in range(cantidad):
            tipo = random.choice(tipos_recurso)
            nombre = ""
            stock = 0
            especialidad = ""
            contacto = ""

            if tipo == Recurso.TIPO_REPUESTO:
                nombre = f"Repuesto {random.choice(['Filtro', 'Válvula', 'Sensor', 'Rodamiento'])} {random.randint(1,100)}"
                stock = random.randint(0, 50)
            elif tipo == Recurso.TIPO_TECNICO:
                nombre = f"Técnico {random.choices(['Juan', 'Ana', 'Carlos', 'Maria'], k=1)[0]} {random.randint(1,99)}"
                especialidad = random.choice(["Eléctrico", "Mecánico", "Hidráulico"])
            elif tipo == Recurso.TIPO_PROVEEDOR:
                nombre = f"Proveedor {random.choice(['Global', 'Tech', 'Servicios', 'Industrial'])} SA"
                contacto = "contacto@proveedor.com"

            Recurso.objects.create(
                nombre=nombre if nombre else f"Recurso-{random.randint(100,999)}",
                tipo=tipo,
                stock=stock,
                stock_minimo=5,
                especialidad=especialidad,
                contacto=contacto,
                disponible=True,
            )
            recursos_creados += 1

        return Response(
            {
                "mensaje": f"Generación completada: {equipos_creados} equipos, {mantenimientos_creados} mant., {recursos_creados} recursos, {eventos_creados} eventos.",
                "detalles": {
                    "equipos": equipos_creados,
                    "mantenimientos": mantenimientos_creados,
                    "recursos": recursos_creados,
                    "eventos": eventos_creados,
                },
            }
        )

    @action(detail=False, methods=["post"])
    def reset_database(self, request):
        """Reset completo de la base de datos"""
        from api.models import (
            Equipo,
            Mantenimiento,
            Recurso,
            Evento,
            AprendizajeAutomatico,
            BaseConocimiento,
            Recomendacion,
        )

        counts = {
            "equipos": Equipo.objects.count(),
            "mantenimientos": Mantenimiento.objects.count(),
            "recursos": Recurso.objects.count(),
            "eventos": Evento.objects.count(),
        }

        Equipo.objects.all().delete()
        Mantenimiento.objects.all().delete()
        Recurso.objects.all().delete()
        Evento.objects.all().delete()
        AprendizajeAutomatico.objects.all().delete()
        BaseConocimiento.objects.all().delete()
        Recomendacion.objects.all().delete()

        return Response({"mensaje": "BD reseteada completamente", "eliminados": counts})

    @action(detail=False, methods=["post"])
    def reset_ia(self, request):
        """Reset del conocimiento de IA"""
        from api.models import AprendizajeAutomatico, BaseConocimiento

        aprendizajes = AprendizajeAutomatico.objects.count()
        conocimiento = BaseConocimiento.objects.count()

        AprendizajeAutomatico.objects.all().delete()
        BaseConocimiento.objects.all().delete()

        return Response(
            {
                "mensaje": "Conocimiento IA reseteado",
                "aprendizajes_eliminados": aprendizajes,
                "conocimiento_eliminado": conocimiento,
            }
        )

    @action(detail=False, methods=["post"])
    def entrenar(self, request):
        """Entrena el sistema IA con los datos actuales"""
        try:
            # Entrenar con todos los mantenimientos completados
            mantenimientos = Mantenimiento.objects.filter(
                estado=4
            )  # 4 = completado (ESTADO_COMPLETADO)

            if mantenimientos.count() == 0:
                return Response(
                    {
                        "mensaje": "No hay mantenimientos completados para entrenar",
                        "entrenados": 0,
                    }
                )

            entrenados = 0
            from api.servicios.ia_core import ia_sistema

            for mant in mantenimientos:
                try:
                    # Datos para aprendizaje
                    dias = (mant.fecha_completada - mant.fecha_programada).days
                    resultado = {
                        "fue_exitoso": True,
                        "dias_resolucion": max(1, dias),
                        "costo_real": float(mant.costo),
                        "costo_esperado": float(mant.costo) * 1.1,  # Estimación
                    }

                    # Entrenar IA
                    ia_sistema.aprender_de_resultado(mant, resultado)
                    entrenados += 1
                except Exception:
                    pass

            return Response(
                {
                    "mensaje": f"IA entrenada con {entrenados} mantenimientos (Estado: COMPLETADO)",
                    "entrenados": entrenados,
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
