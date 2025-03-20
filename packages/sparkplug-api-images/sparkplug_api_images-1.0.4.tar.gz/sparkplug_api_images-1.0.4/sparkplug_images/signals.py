# ruff: noqa: ARG001, ANN001
# django
from django.db.models.signals import pre_save
from django.dispatch import receiver

# app
from .models import Image


@receiver(pre_save, sender=Image)
def image_pre_save(sender, instance, **kwargs) -> None:
    try:
        previous = Image.objects.get(uuid=instance.uuid)
    except Image.DoesNotExist:
        previous = None

    if not previous:
        return

    if previous.file != instance.file:
        previous.file.delete(save=False)
