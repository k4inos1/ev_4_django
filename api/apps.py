from django.apps import AppConfig


class ConfApi(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "API"

    name = "api"

    def ready(self):
        import api.signals
