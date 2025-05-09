# appProtectiOn/apps.py
from django.apps import AppConfig

class AppProtectiOnConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "appProtectiOn"

    def ready(self):
        """
        No hagas consultas a la BD aquí.
        Solo registramos los handlers de señales.
        """
        # Importa el módulo que define los handlers → los registra en runtime.
        # El noqa evita el warning de “import unused”.
        from . import signals  # noqa: F401
