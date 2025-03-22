from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdOrderConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_order"
    verbose_name = _("Order")

    def ready(self):
        import artd_order.signals
