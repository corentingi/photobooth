from typing import List, Tuple

from app.image_filters import ImageFilter


def apply_filters(image, filters: List[ImageFilter]):
    for filter in filters:
        image = filter.process(image)
    return image


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
