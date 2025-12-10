from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "API"

    name = "api"

    def ready(self):
        import api.signals
