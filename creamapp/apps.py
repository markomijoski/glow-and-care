"""
=============================================================================
  Glow & Care — App Configuration
  Registers signals when Django starts up.
=============================================================================
"""

from django.apps import AppConfig


class CreamAppConfig(AppConfig):
    name         = "creamapp"          # replace with your actual app name
    verbose_name = "Glow & Care Store"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """
        Import signals module so all signal receivers are connected
        when Django finishes loading. This must run exactly once.
        """
        import creamapp.signals  
