import abc
from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Tuple

from PIL import Image, ImageDraw

from app.entities import PictureFormat
from app.image_helpers import (
    ensure_size,
    min_common_size,
)
from app.entities import PictureOrientation


def _absolute_margin_from_size(margin: str, size: Tuple[int, int]) -> int:
    if margin.endswith("%"):
        return int(max(*size) * int(margin[0:-1]) / 100)
    else:
        raise NotImplementedError()


class MontageTemplate(abc.ABC):
    capture_count: ClassVar[int]
    format: ClassVar[PictureFormat]
    capture_format: ClassVar[PictureFormat]
    orientation: ClassVar[PictureOrientation]

    def process(self, images, title_image: Optional[Any] = None):
        raise NotImplementedError()


@dataclass
class StripWithTitle(MontageTemplate):
    capture_count: ClassVar[int] = 3
    format: ClassVar[PictureFormat] = PictureFormat.FORMAT_LANDSCAPE_15x5
    capture_format: ClassVar[PictureFormat] = PictureFormat.FORMAT_PORTRAIT_3x4
    orientation: ClassVar[PictureOrientation] = PictureOrientation.PORTRAIT

    background_color: str = "white"
    margin: str = "2%"

    def _montage_size(self, image_size, absolute_margin) -> Tuple[int, int]:
        montage_height = image_size[1] + 2 * absolute_margin
        montage_width = int(montage_height * self.format.value[0] / self.format.value[1])
        return (montage_width, montage_height)

    def process(self, images, title_image: Optional[Any] = None):
        assert len(images) == self.capture_count
        common_image_size = min_common_size(images)
        margins_px = _absolute_margin_from_size(self.margin, common_image_size)
        montage_size = self._montage_size(common_image_size, margins_px)

        montage = Image.new('RGB', size=montage_size, color=self.background_color)

        offset = (margins_px, margins_px)
        for image in images:
            montage.paste(image, offset)
            offset = (
                offset[0] + image.size[0] + margins_px,
                offset[1],
            )

        if title_image is not None:
            title_size = (
                montage_size[0] - offset[0] - margins_px,
                montage_size[1] - offset[1] - margins_px,
            )
            title_image = ensure_size(title_image, title_size, keep_proportions=True)
            montage.paste(
                title_image,
                (
                    offset[0],
                    int((montage_size[1] - title_image.height) / 2)
                ),
            )

        return montage


@dataclass
class DoubleStripWithTitle(MontageTemplate):
    capture_count: ClassVar[int] = 3
    format: ClassVar[PictureFormat] = PictureFormat.FORMAT_LANDSCAPE_15x10
    capture_format: ClassVar[PictureFormat] = PictureFormat.FORMAT_PORTRAIT_3x4
    orientation: ClassVar[PictureOrientation] = PictureOrientation.PORTRAIT

    background_color: str = "white"
    margin: str = "2%"

    def process(self, images, title_image: Optional[Any] = None):
        single_strip = StripWithTitle(
            background_color=self.background_color,
            margin=self.margin,
        ).process(images, title_image)
        montage_size = (single_strip.size[0], single_strip.size[1] * 2)
        montage = Image.new('RGB', size=montage_size, color=self.background_color)
        montage.paste(single_strip, (0, 0))
        montage.paste(single_strip, (0, single_strip.size[1]))

        # Draw a cutting line
        draw = ImageDraw.Draw(montage)
        draw.line([(0, montage_size[1]/2), (montage_size[0], montage_size[1]/2)], fill="white", width=2)

        return montage
