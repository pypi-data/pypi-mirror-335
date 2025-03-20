# app
from .image_teaser import ImageTeaser


class ImageExpanded(
    ImageTeaser,
):
    class Meta(
        ImageTeaser.Meta,
    ):
        fields = (*ImageTeaser.Meta.fields,)

        read_only_fields = ("__all__",)
