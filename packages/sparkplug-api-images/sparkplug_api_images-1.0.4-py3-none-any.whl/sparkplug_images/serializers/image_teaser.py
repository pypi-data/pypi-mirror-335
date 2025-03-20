# python
from typing import TYPE_CHECKING

# django
from django.conf import settings

# contrib
from decouple import config
from sorl.thumbnail import get_thumbnail
from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField,
    SlugRelatedField,
)

# app
from ..models import Image

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


class ImageTeaser(
    ModelSerializer["Image"],
):
    creator_uuid: "SlugRelatedField[type[AbstractBaseUser]]" = SlugRelatedField(
        slug_field="uuid",
        source="creator",
        read_only=True,
    )

    file = SerializerMethodField()

    class Meta:
        model = Image

        fields = (
            "uuid",
            "created",
            "creator_uuid",
            "file",
        )

        read_only_fields = ("__all__",)

    def __init__(self, *args, **kwargs) -> None:
        self.crop = kwargs.pop("crop", False)
        self.thumbnail_size = kwargs.pop(
            "thumbnail_size",
            settings.THUMBNAIL_PRESET_DEFAULT,
        )
        super().__init__(*args, **kwargs)

    def get_file(self, obj: Image) -> str:
        if not obj.file:
            return ""

        file_width = obj.file.width
        file_height = obj.file.height
        landscape = file_width >= file_height

        thumbnail_config = { "quality": 100 }

        if self.crop:
            thumbnail_config["crop"] = "center"
            geometry_string = self.thumbnail_size

        else:
            preset_width, preset_height = self.thumbnail_size.split("x")
            geometry_string = f"x{preset_height}"
            if landscape:
                geometry_string = preset_width

        thumbnail_config["geometry_string"] = geometry_string

        thumbnail = get_thumbnail(
            obj.file,
            **thumbnail_config,
        )

        environment = config("API_ENV")
        thumbnail_url = thumbnail.url
        if environment == "dev":
            thumbnail_url = f"{settings.API_URL}{thumbnail.url}"

        return thumbnail_url
