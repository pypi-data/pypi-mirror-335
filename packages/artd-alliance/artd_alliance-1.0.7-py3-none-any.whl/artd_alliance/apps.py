from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdAllianceConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_alliance"
    verbose_name = _("Alliance")

    def ready(self):
        from artd_alliance import signals  # noqa
