# python
import logging
from PIL import Image


log = logging.getLogger(__name__)


def optimize_image(
    source: str,
    filename: str,
) -> str:
    max_long = 1920
    max_short = 1080
    optimized = False
    filepath = f"/tmp/{filename}.jpg"  # noqa: S108

    with Image.open(source) as source_img:
        img = source_img
        image_width, image_height = img.size

        log.debug(
            "image width/height",
            extra={
                "image_width": image_width,
                "image_height": image_height,
            },
        )

        if image_width < image_height:
            landscape = False
            side_long = image_height
            side_short = image_width
        else:
            landscape = True
            side_long = image_width
            side_short = image_height

        log.debug("landscape", extra={"landscape": landscape})
        log.debug(
            "side long/short",
            extra={
                "side_long": side_long,
                "side_short": side_short,
            },
        )

        if any([
            side_long > max_long,
            side_short > max_short,
        ]):
            scaled_short = int(max_long * (side_short / side_long))
            scaled_long = int(max_short * (side_long / side_short))
            log.debug(
                "scaled long/short",
                extra={
                    "scaled_long": scaled_long,
                    "scaled_short": scaled_short,
                },
            )

            if scaled_short > max_short:
                target_long = scaled_long
                target_short = max_short
            else:
                target_long = max_long
                target_short = scaled_short

            log.debug(
                "target long/short",
                extra={
                    "target_long": target_long,
                    "target_short": target_short,
                },
            )

            if landscape:
                calc_width = target_long
                calc_height = target_short
            else:
                calc_width = target_short
                calc_height = target_long

            log.debug(
                "calc width/height",
                extra={
                    "calc_width": calc_width,
                    "calc_height": calc_height,
                },
            )

            img = img.resize((calc_width, calc_height))
            optimized = True

        if img.format != "JPEG":
            msg = f"converting format {img.format} to JPEG"
            log.debug(msg)
            img = img.convert("RGB")
            optimized = True

        if optimized:
            img.save(filepath, quality=80, optimize=True)

        log.debug("image optimized", extra={ "optimized": optimized })

    return filepath, optimized
