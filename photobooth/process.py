import enum
from pathlib import Path
from typing import List, Optional
from PIL import Image

from image_filters import ImageFilter


class PictureOrientation(enum.Enum):
    PORTRAIT = "PORTRAIT"
    LANDSCAPE = "LANDSCAPE"


class PictureFormat(enum.Enum):
    FORMAT_LANDSCAPE_15x5 = (15, 5)
    FORMAT_LANDSCAPE_4x3 = (4, 3)
    FORMAT_LANDSCAPE_3x2 = (3, 2)
    FORMAT_PORTRAIT_3x4 = (3, 4)


class PhotoMontageType(enum.Enum):
    STRIP_WITH_TITLE = (
        PictureOrientation.PORTRAIT,
        PictureFormat.FORMAT_PORTRAIT_3x4,
        PictureFormat.FORMAT_LANDSCAPE_15x5,
    )


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


def assemble_images(
    images,
    montage_type: PhotoMontageType,
    background_color: str = "white",
    title_image = None,
    filters: List[ImageFilter] = None,
    margins_percent: int = 2,
):
    orientation, image_format, montage_format = montage_type.value
    normalized_images, common_size = normalize_images(
        images=images,
        orientation=orientation,
        image_format=image_format,
    )

    if filters:
        filters = filters or []
        for idx, image in enumerate(normalized_images):
            for filter in filters:
                image = filter.process(image)
            normalized_images[idx] = image

    margins_px = int(max(*common_size) * margins_percent / 100)
    montage_height = common_size[1] + 2 * margins_px
    montage_width = int(montage_height * montage_format.value[0] / montage_format.value[1])
    montage_size = (montage_width, montage_height)

    montage = Image.new('RGB', size=montage_size, color=background_color)

    offset = (margins_px, margins_px)
    for image in normalized_images:
        montage.paste(image, offset)
        offset = (
            offset[0] + image.size[0] + margins_px,
            offset[1],
        )

    # Title image
    if title_image:
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


def process_images(
    captures: List[Path],
    output_path: Path,
    title_image: Optional[Path],
    filters: List[ImageFilter] = None,
):
    images = []
    for capture in captures:
        with Image.open(capture) as image:
            image.load()
            images.append(image)

    if title_image:
        with Image.open(title_image) as title:
            title.load()

    montage = assemble_images(
        images,
        montage_type=PhotoMontageType.STRIP_WITH_TITLE,
        title_image=title,
        filters=filters or [],
        background_color="black",
        margins_percent=4,
    )
    montage.save(output_path)
