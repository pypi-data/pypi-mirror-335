# django
from django.core.validators import FileExtensionValidator

# contrib
from rest_framework import serializers

# app
from ..models import Image


class ImageWrite(
    serializers.ModelSerializer["Image"],
):
    file = serializers.ImageField(
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"],
            ),
        ],
    )

    class Meta:
        model = Image

        fields = (
            "file",
        )
