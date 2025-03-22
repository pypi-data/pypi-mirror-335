from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdSiigoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("SIIGO")
    verbose_name_plural = _("SIIGO")
    name = "artd_siigo"

    def ready(self):
        from artd_siigo import signals  # noqa
