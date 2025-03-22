from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ArtdCustomerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Customer")
    name = "artd_customer"

    def ready(self):
        from artd_customer import signals  # noqa: F401
