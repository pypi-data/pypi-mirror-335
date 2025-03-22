from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def execute_after_migrations(sender, **kwargs):
    from artd_modules.utils import create_or_update_module_row

    create_or_update_module_row(
        slug="artd_customer",
        name="Artd Customer",
        description="Artd Customer",
        version="1.0.17",
        is_plugin=False,
    )
