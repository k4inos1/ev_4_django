"""
Auto-inicializacion del sistema al arrancar Django
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        """Se ejecuta cuando Django esta listo"""
        import os

        if os.environ.get("RUN_MAIN") == "true":
            self.inicializar_sistema()

    def inicializar_sistema(self):
        """Inicializa todo el sistema automaticamente"""
        try:
            from api.servicios.ia_core import ia_sistema

            # Solo cargar sistema IA (sin acceso a BD)
            ia_sistema.obtener_estadisticas()

        except Exception:
            pass  # Silencioso
