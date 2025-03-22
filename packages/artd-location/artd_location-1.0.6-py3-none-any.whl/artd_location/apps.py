from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ArtdLocationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_location"
    verbose_name = _("Location")

    def ready(self) -> None:
        from artd_location import signals  # noqa: F401
