from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdStockConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_stock"
    verbose_name = _("Stock")

    def ready(self):
        from . import signals  # noqa: F401

        pass
