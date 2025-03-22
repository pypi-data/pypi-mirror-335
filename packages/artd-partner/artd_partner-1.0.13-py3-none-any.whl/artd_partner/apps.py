from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdPartnerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Partner")
    name = "artd_partner"

    def ready(self):
        from artd_partner import signals  # noqa: F401
