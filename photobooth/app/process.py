from functools import cached_property
from pathlib import Path
from PIL import Image, ImageOps
from typing import List

from app import image_filters, templates
from app.config import ProcessingConfig, TemplateConfig
from app.image_helpers import apply_filters, ensure_size, min_common_size, resized
from app.entities import PictureFormat, PictureOrientation


def get_orientation(image) -> PictureOrientation:
    width, height = image.size
    if width > height:
        return PictureOrientation.LANDSCAPE
    return PictureOrientation.PORTRAIT


def ensure_orientation(image, orientation: PictureOrientation):
    if (get_orientation(image) != orientation):
        return image.transpose(method=Image.Transpose.ROTATE_90)
    return image


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


def load_image(path: Path):
    with Image.open(path) as image:
        image.load()
    return image


class CaptureProcessor:
    def __init__(self, settings: ProcessingConfig, presets: List[TemplateConfig]) -> None:
        self.settings = settings
        self.presets = presets

    @cached_property
    def template(self) -> templates.MontageTemplate:
        try:
            template = self.settings.template or self.presets[self.settings.preset].template
            return getattr(templates, template.name)(**template.params)
        except Exception as e:
            raise Exception("Could not find template from provided configuration") from e

    @property
    def capture_filters(self):
        filters = self.settings.filters
        if not filters:
            filters = self.presets[self.settings.preset].filters
        return [
            getattr(image_filters, filter.name)(**filter.params)
            for filter in filters
        ]

    @property
    def title_filters(self):
        filters = self.settings.title.filters
        if not filters:
            filters = self.presets[self.settings.preset].title_filters
        return [
            getattr(image_filters, filter.name)(**filter.params)
            for filter in filters
        ]

    def process(
        self,
        captures: List[Path],
        output_file_path: Path,
    ):
        processed_images = self._pre_process_captures(captures)
        title_image = self._pre_process_title()

        montage = self.template.process(processed_images, title_image)
        montage.save(output_file_path)

    def _pre_process_captures(
        self,
        captures: List[Path],
    ):
        images = [load_image(path) for path in captures]

        # Make sure images are in the right orientation
        images = [ImageOps.exif_transpose(image) for image in images]

        if self.settings.correct_orientation:
            images = [ensure_orientation(image, self.template.orientation) for image in images]

        # Crop images to the right format
        images = [ensure_format(image, self.template.capture_format) for image in images]

        # Resize all images to the same size
        common_size = min_common_size(images)
        images = [ensure_size(image, common_size) for image in images]

        # Apply filters on captures
        images = [apply_filters(image, self.capture_filters) for image in images]

        return images

    def _pre_process_title(self):
        if not self.settings.title:
            return None
        with Image.open(self.settings.title.image_path) as title:
            title.load()
        return apply_filters(title, self.title_filters)
