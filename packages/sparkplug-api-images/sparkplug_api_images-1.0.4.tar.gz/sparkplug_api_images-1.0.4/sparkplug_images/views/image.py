# python
import logging

# contrib
from djangorestframework_camel_case.parser import (
    CamelCaseMultiPartParser,
)
from rest_framework import viewsets

# sparkplug
from sparkplug_core.views import CreateUpdateView

# app
from .. import (
    models,
    permissions,
    tasks,
)
from ..serializers import (
    ImageExpanded,
    ImageTeaser,
    ImageWrite,
)


log = logging.getLogger(__name__)


class Image(
    CreateUpdateView,
    viewsets.GenericViewSet,
):
    model = models.Image

    retrieve_serializer_class = ImageExpanded
    list_serializer_class = ImageTeaser
    write_serializer_class = ImageWrite

    permission_classes = (permissions.Image,)

    parser_classes = (CamelCaseMultiPartParser,)

    def perform_create(self, serializer: ImageWrite) -> None:
        user = self.request.user
        instance = serializer.save(creator=user)
        tasks.process_image(instance.uuid)()

    def perform_update(self, serializer: ImageWrite) -> None:
        instance = serializer.save()
        tasks.process_image(instance.uuid)()
