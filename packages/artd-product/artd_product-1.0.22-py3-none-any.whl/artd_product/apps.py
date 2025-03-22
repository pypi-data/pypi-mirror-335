from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdProductConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Product")
    name = "artd_product"

    def ready(self):
        from artd_product import signals  # noqa: F401
