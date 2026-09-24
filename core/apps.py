from django.apps import AppConfig


def _watch_env_file(sender, **kwargs):
    """`.env` o'zgarsa, dev-server o'zi qayta ishga tushsin."""
    from django.conf import settings

    sender.watch_dir(settings.BASE_DIR, ".env")


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from django.utils.autoreload import autoreload_started

        autoreload_started.connect(_watch_env_file)
