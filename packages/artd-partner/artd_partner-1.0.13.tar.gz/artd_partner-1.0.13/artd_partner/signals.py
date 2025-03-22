from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def execute_after_migrations(sender, **kwargs):
    from artd_modules.utils import create_or_update_module_row

    create_or_update_module_row(
        slug="artd_partner",
        name="ArtD Partner",
        description="ArtD Partner",
        version="1.0.13",
        is_plugin=False,
    )
