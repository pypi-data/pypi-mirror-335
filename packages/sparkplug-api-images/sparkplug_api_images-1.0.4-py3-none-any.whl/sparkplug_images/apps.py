from django.apps import AppConfig


class ImageConfig(AppConfig):
    name = "sparkplug_images"

    def ready(self) -> None:
        from . import signals  # noqa: F401
