from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdUrlsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_urls"
    verbose_name = _("Urls")

    def ready(self):
        from artd_urls import signals  # noqa
