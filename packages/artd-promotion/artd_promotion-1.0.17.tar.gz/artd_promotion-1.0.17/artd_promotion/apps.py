from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdPromotionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_promotion"
    verbose_name = _("Promotion")

    def ready(self):
        from artd_promotion import signals  # noqa
