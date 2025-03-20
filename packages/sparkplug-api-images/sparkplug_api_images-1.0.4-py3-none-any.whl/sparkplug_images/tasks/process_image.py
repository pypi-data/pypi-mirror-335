# python
import logging
from pathlib import Path

# django
from django.core.files import File

# contrib
from decouple import config
from huey.contrib.djhuey import task

# app
from .. import (
    models,
    services,
)


log = logging.getLogger(__name__)


@task()
def process_image(
    image_uuid: str,
) -> None:

    try:
        instance = models.Image.objects.get(uuid=image_uuid)
    except models.Image.DoesNotExist:
        return

    if bool(instance.file) is False:
        return

    log.debug(
        "process image",
        extra={ "image_uuid": instance.uuid },
    )

    environment = config("API_ENV")

    source = instance.file.url
    if environment == "dev":
        source = instance.file.path

    log.debug(
        "image source",
        extra={ "image_source": source },
    )

    try:
        filepath, optimized = services.optimize_image(
            source=source,
            filename=instance.uuid,
        )

        if not optimized:
            return

        with Path.open(filepath, "rb") as f:
            file = File(f)
            filename = Path(filepath).name

            if instance.file:
                instance.file.delete()

            instance.file.save(filename, file)

    except FileNotFoundError:
        log.exception(
            "Failed to optimize image",
            extra={
                "image_uuid": instance.uuid,
                "image_source": source,
            },
        )
