from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdServiceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_service"
    verbose_name = _("Service")

    def ready(self):
        import artd_service.signals  # noqa
