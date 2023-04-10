from pathlib import Path
from typing import List, Tuple
from PIL import Image

from app.config import ProcessingConfig
from app.image_filters import ImageFilter
from app.entities import PhotoMontageType, PictureFormat, PictureOrientation
from photobooth.app import image_filters


def get_orientation(image) -> PictureOrientation:
    width, height = image.size
    if width > height:
        return PictureOrientation.LANDSCAPE
    return PictureOrientation.PORTRAIT


def ensure_orientation(image, orientation: PictureOrientation):
    if (get_orientation(image) != orientation):
        return image.transpose(method=Image.Transpose.ROTATE_90)
    return image


def resized(image_size, format, crop: bool = True):
    output_ratio = format[0] / format[1]
    image_width, image_height = image_size
    image_ratio = image_width / image_height

    if crop == (output_ratio > image_ratio):
        output_width = image_width
        output_height = int(output_width / output_ratio)
    else:
        output_height = image_height
        output_width = int(output_height * output_ratio)

    return (output_width, output_height)


def ensure_format(image, format: PictureFormat):
    image_width, image_height = image.size
    output_width, output_height = resized(image.size, format.value)

    left_margin = (image_width - output_width) / 2
    upper_margin = (image_height - output_height) / 2

    return image.crop((
        left_margin,
        upper_margin,
        left_margin + output_width,
        upper_margin + output_height,
    ))


def ensure_size(image, size, keep_proportions: bool = False):
    if image.size == size:
        return image
    if keep_proportions:
        resized_size = resized(size, image.size, crop=True)
        size = (
            min(resized_size[0], size[0]),
            min(resized_size[1], size[1]),
        )
    return image.resize(size)


def min_common_size(images) -> Tuple[int]:
    return (
        min(image.size[0] for image in images),
        min(image.size[1] for image in images),
    )


def normalize_images(
    images,
    orientation: PictureOrientation,
    image_format: PictureFormat,
    rotate: bool = False,
):
    if rotate:
        images = [
            ensure_orientation(image, orientation)
            for image in images
        ]
    images = [
        ensure_format(image, image_format)
        for image in images
    ]
    common_size = (
        min(image.size[0] for image in images),
        min(image.size[1] for image in images),
    )
    images = [
        ensure_size(image, common_size)
        for image in images
    ]
    return images, common_size


def apply_filters(image, filters: List[ImageFilter]):
    for filter in filters:
        image = filter.process(image)
    return image


def load_image(path: Path):
    with Image.open(path) as image:
        image.load()
    return image


class CaptureProcessor:
    def __init__(self, settings: ProcessingConfig) -> None:
        self.settings = settings

    @property
    def capture_filters(self):
        return [
            getattr(image_filters, filter.name)(**filter.params)
            for filter in self.settings.captures.filters
        ]

    @property
    def title_filters(self):
        return [
            getattr(image_filters, filter.name)(**filter.params)
            for filter in self.settings.title.filters
        ]

    def process(
        self,
        captures: List[Path],
        output_file_path: Path,
    ):
        # TODO: Handle templates in classes
        assert self.settings.template.name == PhotoMontageType.STRIP_WITH_TITLE.name

        processed_images = self._pre_process_captures(captures)
        montage = self._assemble_captures(processed_images)
        montage.save(output_file_path)

    def _pre_process_captures(
        self,
        captures: List[Path],
    ):
        orientation, image_format, _ = self.settings.template.value

        images = [load_image(path) for path in captures]

        if self.settings.captures.correct_orientation:
            images = [ensure_orientation(image, orientation) for image in images]

        # Crop images to the right format
        images = [ensure_format(image, image_format) for image in images]

        # Resize all images to the same size
        common_size = min_common_size(images)
        images = [ensure_size(image, common_size) for image in images]

        # Apply filters on captures
        images = [apply_filters(image, self.capture_filters) for image in images]

        return images

    def _assemble_captures(
        self,
        images,
    ):
        common_size = min_common_size(images)
        _, _, montage_format = self.settings.template.value

        margins_px = int(max(*common_size) * self.settings.captures.margin / 100)
        montage_height = common_size[1] + 2 * margins_px
        montage_width = int(montage_height * montage_format.value[0] / montage_format.value[1])
        montage_size = (montage_width, montage_height)

        montage = Image.new('RGB', size=montage_size, color=self.settings.background.color)

        offset = (margins_px, margins_px)
        for image in images:
            montage.paste(image, offset)
            offset = (
                offset[0] + image.size[0] + margins_px,
                offset[1],
            )

        if self.settings.title.image_path:
            with Image.open(self.settings.title.image_path) as title_image:
                title_image.load()

            title_size = (
                montage_size[0] - offset[0] - margins_px,
                montage_size[1] - offset[1] - margins_px,
            )
            title_image = ensure_size(title_image, title_size, keep_proportions=True)
            title_image = apply_filters(title_image, filters=self.title_filters)
            montage.paste(
                title_image,
                (
                    offset[0],
                    int((montage_size[1] - title_image.height) / 2)
                ),
            )

        return montage
