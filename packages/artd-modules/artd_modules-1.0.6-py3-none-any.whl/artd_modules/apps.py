from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdModulesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "artd_modules"
    verbose_name = _("Modules")

    def ready(self):
        import artd_modules.signals  # noqa
