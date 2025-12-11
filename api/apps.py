"""
Auto-inicializacion del sistema al arrancar Django
"""

from django.apps import AppConfig
from django.conf import settings


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        """Se ejecuta cuando Django esta listo"""
        # Solo ejecutar en el proceso principal (no en reloader)
        import os

        if os.environ.get("RUN_MAIN") == "true":
            self.inicializar_sistema()

    def inicializar_sistema(self):
        """Inicializa todo el sistema automaticamente"""
        try:
            from api.servicios.ia_core import ia_sistema
            from api.models import ModeloIA, Equipo

            print("\n" + "=" * 60)
            print("INICIALIZANDO SISTEMA INTELIGENTE")
            print("=" * 60)

            # 1. Verificar/Crear modelo IA
            modelo, created = ModeloIA.objects.get_or_create(
                nombre="EV4-ML-Model",
                defaults={"version": "1.0.0", "estado": "idle", "activo": True},
            )

            if created:
                print("[OK] Modelo IA creado")
            else:
                print("[OK] Modelo IA cargado")

            # 2. Cargar sistema IA
            stats = ia_sistema.obtener_estadisticas()
            print(f"[OK] Sistema IA: {stats['total_estados']} estados")
            print(
                f"[OK] Rust: {'Habilitado' if stats['rust_habilitado'] else 'Deshabilitado'}"
            )

            # 3. Verificar datos
            equipos = Equipo.objects.count()
            print(f"[OK] Equipos en BD: {equipos}")

            if equipos == 0:
                print("[INFO] BD vacia - ejecuta: python manage.py aprender_web")

            print("=" * 60)
            print("SISTEMA LISTO")
            print("Dashboard: http://127.0.0.1:8000/")
            print("API: http://127.0.0.1:8000/api/")
            print("Docs: http://127.0.0.1:8000/api/docs/")
            print("=" * 60 + "\n")

        except Exception as e:
            print(f"[ERROR] Inicializacion: {e}")
