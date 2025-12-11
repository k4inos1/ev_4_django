"""
Vistas Analíticas para Consultas Relevantes
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from api.models import (
    Equipo,
    Mantenimiento,
    AprendizajeAutomatico,
    BaseConocimiento,
    Mantenimiento,
    AprendizajeAutomatico,
    BaseConocimiento,
    Recomendacion,
    Recurso,
    Evento,
)
from django.db.models import Sum


class AnalyticsViewSet(viewsets.ViewSet):
    """Vistas analíticas y consultas útiles"""

    @action(detail=False, methods=["get"])
    def resumen_general(self, request):
        """Resumen general del sistema"""
        return Response(
            {
                "equipos": {
                    "total": Equipo.objects.count(),
                    "criticos": Equipo.objects.filter(es_critico=True).count(),
                    "por_categoria": list(
                        Equipo.objects.values("categoria").annotate(total=Count("id"))
                    ),
                },
                "mantenimientos": {
                    "total": Mantenimiento.objects.count(),
                    "pendientes": Mantenimiento.objects.filter(
                        estado=1
                    ).count(),  # 1 = pendiente
                    "completados": Mantenimiento.objects.filter(
                        estado=3
                    ).count(),  # 3 = completado
                    "prioridad_promedio": Mantenimiento.objects.aggregate(
                        Avg("prioridad")
                    )["prioridad__avg"],
                },
                "recursos": {
                    "total": Recurso.objects.count(),
                    "stock_bajo": Recurso.objects.filter(stock__lte=5).count(),
                },
                "eventos": {
                    "total": Evento.objects.count(),
                    "no_resueltos": Evento.objects.filter(resuelto=False).count(),
                    "criticos": Evento.objects.filter(severidad__gte=8).count(),
                },
                "ia": {
                    "aprendizajes": AprendizajeAutomatico.objects.count(),
                    "conocimiento_web": BaseConocimiento.objects.count(),
                    "recomendaciones": Recomendacion.objects.filter(
                        vista=False
                    ).count(),
                    "precision_promedio": AprendizajeAutomatico.objects.aggregate(
                        Avg("precision_prediccion")
                    )["precision_prediccion__avg"]
                    or 0,
                },
            }
        )

    @action(detail=False, methods=["get"])
    def equipos_criticos(self, request):
        """Equipos críticos con mantenimientos pendientes"""
        equipos = Equipo.objects.filter(
            es_critico=True, mantenimientos__estado=1  # 1 = pendiente
        ).distinct()

        resultado = []
        for eq in equipos:
            pendientes = eq.mantenimientos.filter(estado=1).count()  # 1 = pendiente
            resultado.append(
                {
                    "id": eq.id,
                    "nombre": eq.nombre,
                    "empresa": eq.empresa_nombre,
                    "mantenimientos_pendientes": pendientes,
                    "prioridad_maxima": eq.mantenimientos.filter(
                        estado=1  # 1 = pendiente
                    ).aggregate(Avg("prioridad"))["prioridad__avg"]
                    or 0,
                }
            )

        return Response(
            {
                "total": len(resultado),
                "equipos": sorted(
                    resultado,
                    key=lambda x: x["mantenimientos_pendientes"],
                    reverse=True,
                ),
            }
        )

    @action(detail=False, methods=["get"])
    def evolucion_ia(self, request):
        """Evolución del aprendizaje de IA"""
        aprendizajes = AprendizajeAutomatico.objects.order_by("fecha_aprendizaje")[:50]

        return Response(
            {
                "total_aprendizajes": aprendizajes.count(),
                "evolucion": [
                    {
                        "fecha": a.fecha_aprendizaje.isoformat(),
                        "precision": a.precision_prediccion,
                        "mejora": a.mejora_obtenida,
                    }
                    for a in aprendizajes
                ],
                "precision_actual": (
                    aprendizajes.last().precision_prediccion if aprendizajes else 0
                ),
            }
        )

    @action(detail=False, methods=["get"])
    def conocimiento_web(self, request):
        """Conocimiento adquirido de la web"""
        conocimiento = BaseConocimiento.objects.order_by("-relevancia_score")[:20]

        return Response(
            {
                "total": BaseConocimiento.objects.count(),
                "top_conocimiento": [
                    {
                        "titulo": c.titulo,
                        "fuente": c.fuente_url,
                        "relevancia": c.relevancia_score,
                    }
                    for c in conocimiento
                ],
            }
        )

    @action(detail=False, methods=["get"])
    def predicciones_ia(self, request):
        """Predicciones y recomendaciones activas"""
        recomendaciones = Recomendacion.objects.filter(vista=False).order_by(
            "-confianza"
        )[:10]

        return Response(
            {
                "total_activas": recomendaciones.count(),
                "recomendaciones": [
                    {
                        "titulo": r.titulo,
                        "tipo": r.tipo,
                        "confianza": r.confianza,
                        "equipo_id": r.equipo_id,
                        "descripcion": r.descripcion,
                    }
                    for r in recomendaciones
                ],
            }
        )

    @action(detail=False, methods=["get"])
    def metricas_ml(self, request):
        """Métricas de Machine Learning"""
        from api.servicios.ia_core import ia_sistema

        stats = ia_sistema.obtener_estadisticas()

        return Response(
            {
                "sistema": {
                    "estado": ia_sistema.estado,
                    "learning_rate": ia_sistema.learning_rate,
                    "epsilon": ia_sistema.epsilon,
                    "discount_factor": ia_sistema.discount_factor,
                },
                "metricas": ia_sistema.metricas,
                "estadisticas": stats,
            }
        )

    @action(detail=False, methods=["get"])
    def resumen_costos(self, request):
        """Resumen financiero de mantenimientos"""
        total_costo = Mantenimiento.objects.aggregate(Sum("costo"))["costo__sum"] or 0
        por_tipo = (
            Mantenimiento.objects.values("tipo")
            .annotate(total=Sum("costo"))
            .order_by("-total")
        )

        return Response(
            {
                "total_acumulado": total_costo,
                "desglose_tipo": list(por_tipo),
                "promedio_mantenimiento": total_costo
                / (Mantenimiento.objects.count() or 1),
            }
        )

    @action(detail=False, methods=["get"])
    def alertas_stock(self, request):
        """Recursos con stock crítico"""
        recursos = Recurso.objects.filter(stock__lte=5).order_by("stock")[:10]
        data = [
            {
                "id": r.id,
                "nombre": r.nombre,
                "stock": r.stock,
                "tipo": r.tipo,
                "contacto": r.contacto,
            }
            for r in recursos
        ]
        return Response(data)

    @action(detail=False, methods=["get"])
    def eventos_recientes(self, request):
        """Timeline de eventos"""
        eventos = Evento.objects.all().order_by("-id")[:20]
        data = [
            {
                "id": e.id,
                "tipo": e.tipo,
                "descripcion": e.descripcion,
                "severidad": e.severidad,
                "resuelto": e.resuelto,
                "equipo": e.equipo.nombre if e.equipo else "Sistema",
            }
            for e in eventos
        ]
        return Response(data)

    @action(detail=False, methods=["get"])
    def conocimiento_list(self, request):
        """Lista completa de conocimiento adquirido"""
        items = BaseConocimiento.objects.all().order_by("-fecha_scraping")[:50]
        return Response(
            [
                {
                    "id": i.id,
                    "titulo": i.titulo,
                    "fuente": i.fuente_url,
                    "fecha": i.fecha_scraping,
                    "resumen": i.contenido[:100] + "..." if i.contenido else "",
                }
                for i in items
            ]
        )
