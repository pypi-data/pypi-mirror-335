from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChannelsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Channel")
    name = "artd_channels"

    def ready(self):
        from artd_channels import signals  # noqa: F401
