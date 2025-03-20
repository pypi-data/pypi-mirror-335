from rest_framework import serializers

from ..models import Image


class ImageUUIDField(serializers.SlugRelatedField):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("queryset", Image.objects.all())
        kwargs.setdefault("slug_field", "uuid")
        kwargs.setdefault("source", "image")
        super().__init__(**kwargs)
