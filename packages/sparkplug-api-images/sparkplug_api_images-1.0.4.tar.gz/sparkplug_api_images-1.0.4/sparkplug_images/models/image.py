# django
from django.conf import settings
from django.db import models

# contrib
from sorl.thumbnail import ImageField

# sparkplug
from sparkplug_core.models import BaseModel

# app
from .. import uploads


class Image(
    BaseModel,
):
    creator = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="+",
    )

    file = ImageField(
        upload_to=uploads.file_location,
    )

    class Meta:
        indexes = (models.Index(fields=["uuid"]),)

    def __str__(self) -> str:
        return self.uuid

    def delete(self, *args, **kwargs) -> None:
        self.file.delete()
        super().delete(*args, **kwargs)
