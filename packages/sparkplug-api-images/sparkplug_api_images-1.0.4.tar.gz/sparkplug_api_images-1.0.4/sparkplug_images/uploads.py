# python
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Image


def file_location(instance: "Image", filename: str) -> str:
    path = Path(filename)
    extension = path.suffix

    # cast from float to int to remove decimal precision
    timestamp = int(time.time())

    # create unique filenames to avoid stale cache
    filename = f"{instance.uuid}-{timestamp}"

    return f"images/{filename}{extension}"
