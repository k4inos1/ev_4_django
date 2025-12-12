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
        from api.models import Equipo, Mantenimiento, Recurso, Evento, BaseConocimiento
        from api.servicios.recomendaciones import motor_recomendaciones

        cantidad = request.data.get("cantidad", 10)

        # Cargar conocimiento real para usar en generación
        conocimiento_real = list(
            BaseConocimiento.objects.values_list("titulo", flat=True)
        )
        if not conocimiento_real:
            conocimiento_real = [
                "Mantenimiento preventivo",
                "Revisión general",
                "Ajuste de sensores",
            ]

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

        eventos_preview = []
        equipos_preview = []
        mant_preview = []

        is_preview = request.data.get("preview", False)

        # 1. Generar Equipos INTELIGENTES
        # Intentar inferir categoría basada en el conocimiento
        conocimiento_full = list(BaseConocimiento.objects.all())

        for i in range(cantidad):
            # Selección inteligente de tema
            tema_base = random.choice(conocimiento_full) if conocimiento_full else None

            # Determinar categoría de equipo según palabras clave en el conocimiento
            cat_equipo = random.randint(1, 5)  # Default
            nombre_pfx = "Equipo"

            if tema_base:
                txt = tema_base.titulo.lower() + tema_base.contenido.lower()
                if "bomba" in txt:
                    cat_equipo = 1
                    nombre_pfx = "Bomba"
                elif "motor" in txt:
                    cat_equipo = 2
                    nombre_pfx = "Motor"
                elif "compresor" in txt:
                    cat_equipo = 3
                    nombre_pfx = "Compresor"
                elif "generador" in txt:
                    cat_equipo = 4
                    nombre_pfx = "Generador"

            eq_data = {
                "nombre": f"{nombre_pfx}-{random.randint(100,999)}",
                "empresa_nombre": random.choice(empresas),
                "categoria": cat_equipo,
                "numero_serie": f"SN-{random.randint(100000,999999)}",
                "ubicacion": f"Planta {random.randint(1,5)} - Sector {random.choice(['A','B','C'])}",
                "es_critico": random.choice([True, False]),
                "estado": random.choice(["operativo", "mantenimiento", "detenido"]),
                "fecha_instalacion": timezone.now()
                - timedelta(days=random.randint(30, 1000)),
            }

            if is_preview:
                equipos_preview.append(eq_data)
                eq = Equipo(**eq_data)
                eq.id = i + 1
            else:
                eq = Equipo.objects.create(**eq_data)
                equipos_creados += 1

            # 2. Generar Mantenimientos CONTEXTUALES
            # Usar fragmentos del conocimiento real para la descripción
            desc_mant = "Mantenimiento estándar programado"
            if tema_base:
                # Extraer una frase relevante del contenido (simulado por slice simple por ahora)
                # En un sistema real usaríamos NLP para extraer la oración más relevante
                contenido_limpio = tema_base.contenido[:300].replace("\n", " ")
                desc_mant = f"Ejecución basada en procedimiento: {tema_base.titulo[:50]}... Detalle: {contenido_limpio[:100]}..."

            for j in range(random.randint(1, 2)):  # Menos cantidad, más calidad
                estado_mant = random.choice([1, 2, 4])
                mant_data = {
                    "equipo": eq,
                    "descripcion": desc_mant,
                    "tipo": random.choice(["preventivo", "correctivo", "inspeccion"]),
                    "prioridad": (
                        int(tema_base.relevancia_score * 100)
                        if tema_base
                        else random.randint(10, 90)
                    ),
                    "estado": estado_mant,
                    "fecha_programada": timezone.now()
                    + timedelta(days=random.randint(1, 90)),
                    "fecha_completada": (
                        (timezone.now() - timedelta(days=random.randint(1, 30)))
                        if estado_mant == 4
                        else None
                    ),
                    "tecnico_asignado": f"Técnico-{random.randint(1,10)}",
                    "costo": random.uniform(500.0, 8000.0),  # Costos más realistas
                }

                if is_preview:
                    m_json = mant_data.copy()
                    m_json["equipo"] = eq.nombre
                    m_json["fecha_programada"] = str(mant_data["fecha_programada"])
                    m_json["fecha_completada"] = (
                        str(mant_data["fecha_completada"])
                        if mant_data["fecha_completada"]
                        else None
                    )
                    mant_preview.append(m_json)
                else:
                    Mantenimiento.objects.create(**mant_data)
                    mantenimientos_creados += 1

            # 3. Generar Eventos (Vinculados al tema)
            if random.random() > 0.4:
                desc_evt = (
                    f"Alerta detectada: {tema_base.titulo}"
                    if tema_base
                    else "Alerta de sistema general"
                )
                evt_data = {
                    "tipo": random.choice(
                        [
                            Evento.TIPO_INCIDENTE,
                            Evento.TIPO_TELEMETRIA,
                            Evento.TIPO_FLUJO,
                        ]
                    ),
                    "equipo": eq,
                    "severidad": random.randint(3, 9),
                    "descripcion": desc_evt,
                    "resuelto": random.choice([True, False]),
                }

                if is_preview:
                    e_json = evt_data.copy()
                    e_json["equipo"] = eq.nombre
                    eventos_preview.append(e_json)
                else:
                    Evento.objects.create(**evt_data)
                    eventos_creados += 1

            if not is_preview:
                # 4. Trigger Recomendaciones (solo si no es preview)
                try:
                    motor_recomendaciones.generar_recomendaciones_equipo(eq.id)
                except Exception:
                    pass

        # 5. Generar Recursos (Independientes pero integrados en el flujo)
        tipos_recurso_list = [
            Recurso.TIPO_REPUESTO,
            Recurso.TIPO_TECNICO,
            Recurso.TIPO_PROVEEDOR,
        ]
        recursos_preview = []

        for _ in range(cantidad):  # Generar misma cantidad de recursos que equipos
            tipo = random.choice(tipos_recurso_list)
            nombre = ""
            stock = 0
            especialidad = ""
            contacto = ""

            if tipo == Recurso.TIPO_REPUESTO:
                # Usar conocimiento para nombres de repuestos más reales si existe
                base_name = random.choice(["Filtro", "Válvula", "Sensor", "Rodamiento"])
                if conocimiento_full:
                    # Intento simple de extracción de contexto
                    ctx = random.choice(conocimiento_full).titulo
                    if "Bomba" in ctx:
                        base_name = "Sello Mecánico"
                    elif "Motor" in ctx:
                        base_name = "Rodamiento Aislado"

                nombre = f"Repuesto {base_name} {random.randint(1,100)}"
                stock = random.randint(0, 50)
            elif tipo == Recurso.TIPO_TECNICO:
                nombre = f"Técnico {random.choices(['Juan', 'Ana', 'Carlos', 'Maria'], k=1)[0]} {random.randint(1,99)}"
                especialidad = random.choice(["Eléctrico", "Mecánico", "Hidráulico"])
            elif tipo == Recurso.TIPO_PROVEEDOR:
                nombre = f"Proveedor {random.choice(['Global', 'Tech', 'Servicios', 'Industrial'])} SA"
                contacto = "contacto@proveedor.com"

            r_data = {
                "nombre": nombre if nombre else f"Recurso-{random.randint(100,999)}",
                "tipo": tipo,
                "stock": stock,
                "stock_minimo": 5,
                "especialidad": especialidad,
                "contacto": contacto,
                "disponible": True,
            }

            if is_preview:
                recursos_preview.append(r_data)
            else:
                Recurso.objects.create(**r_data)
                recursos_creados += 1

        if is_preview:
            return Response(
                {
                    "preview": True,
                    "equipos": equipos_preview,
                    "mantenimientos": mant_preview,
                    "eventos": eventos_preview,
                    "recursos": recursos_preview,
                }
            )

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

    @action(detail=False, methods=["post"])
    def aprender_web(self, request):
        """Dispara proceso de aprendizaje web"""
        try:
            # Opción 1: Categoría predefinida
            categoria_id = request.data.get("categoria", 0)
            # Opción 2: Prompt personalizado
            custom_prompt = request.data.get("prompt", None)

            temas = {
                1: "Mejores prácticas mantenimiento predictivo bombas centrífugas industriales API 610 vibraciones",
                2: "Fallas comunes estator rotor motores eléctricos trifásicos inducción análisis termográfico",
                3: "Plan mantenimiento compresores tornillo rotativo industrial preventivo filtros aceite",
                4: "Diagnóstico fallas generadores eléctricos diésel sistema inyección AVR",
                0: "Tecnologías emergentes mantenimiento industrial 4.0 IoT sensores",
            }

            if custom_prompt:
                tema = custom_prompt
            else:
                tema = temas.get(int(categoria_id), temas[0])

            from api.servicios.ia_core import ia_sistema

            resultados = ia_sistema.aprender_de_web(tema, max_resultados=3)

            return Response(
                {
                    "mensaje": f"Aprendizaje completado sobre: {tema}",
                    "resultados": resultados,
                }
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"])
    def gestionar_conocimiento(self, request):
        """Permite borrar items de conocimiento"""
        try:
            accion = request.data.get("accion")
            ids = request.data.get("ids", [])
            from api.models import BaseConocimiento

            if accion == "delete" and ids:
                cant, _ = BaseConocimiento.objects.filter(id__in=ids).delete()
                return Response(
                    {"mensaje": f"Se eliminaron {cant} elementos de conocimiento"}
                )

            return Response({"error": "Acción no válida o sin IDs"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"])
    def ejecutar_automata(self, request):
        """Ejecuta el ciclo de autómata (acciones autónomas)"""
        try:
            from api.servicios.automata import AutomataInteligente

            resultado = AutomataInteligente.ejecutar_ciclo_autonomo()
            return Response(resultado)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"])
    def chat_ia(self, request):
        """Chat con el asistente IA"""
        try:
            mensaje = request.data.get("mensaje", "")
            from api.servicios.chat_service import ChatService

            respuesta = ChatService.procesar_mensaje(mensaje)
            return Response({"respuesta": respuesta})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=["post"])
    def entrenar_cortex(self, request):
        """Entrena la Red Neuronal con historial real"""
        try:
            from api.servicios.cortex_service import CortexService

            loss = CortexService.entrenar_con_historia()
            return Response(
                {
                    "mensaje": "Núcleo Cortex re-calibrado",
                    "loss_final": f"{loss:.4f}",
                    "estado": "Red Neuronal Operativa",
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=500)
