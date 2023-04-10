import abc
from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy
from PIL import Image, ImageEnhance, ImageOps


class ImageFilter(abc.ABC):
    def process(self, image):
        pass


@dataclass
class BlackAndWhite(ImageFilter):
    def process(self, image):
        filter = ImageEnhance.Color(image)
        return filter.enhance(0)


@dataclass
class Inverted(ImageFilter):
    def process(self, image):
        if image.mode == 'RGBA':
            r, g, b, a = image.split()
            inverted_image = ImageOps.invert(
                Image.merge('RGB', (r, g, b))
            )

            r2, g2, b2 = inverted_image.split()
            return Image.merge('RGBA', (r2, g2, b2, a))
        return ImageOps.invert(image)


@dataclass
class LevelImage(ImageFilter):
    black: int = 2
    white: int = 2
    level: int = 0

    def process(self, image):
        image_array = numpy.asarray(image, numpy.uint8)
        hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        h,s,v = cv2.split(hsv)
        floor = numpy.percentile(v, self.level or self.black) # 5% of pixels will be black
        ceil = numpy.percentile(v, 100 - (self.level or self.white)) # 5% of pixels will be white
        a = 255 / (ceil - floor)
        b = floor * 255 / (floor - ceil)
        v = numpy.maximum(0, numpy.minimum(255 , v * a + b)).astype(numpy.uint8)
        hsv = cv2.merge((h,s,v))
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

        return Image.fromarray(rgb)


@dataclass
class ColorLevel(ImageFilter):
    red: Tuple[int, int] = (0, 255)
    green: Tuple[int, int] = (0, 255)
    blue: Tuple[int, int] = (0, 255)

    @staticmethod
    def _linear_level_channel(values, scale):
        floor, ceil = scale
        slope = 255 / (ceil - floor)
        offset = floor * 255 / (floor - ceil)
        return numpy.maximum(0, numpy.minimum(255 , values * slope + offset)).astype(numpy.uint8)

    def process(self, image):
        if self.red == (0, 255) and self.green == (0, 255) and self.blue == (0, 255):
            return image

        rgb = numpy.asarray(image, numpy.uint8)
        r, g, b = cv2.split(rgb)

        if self.red != (0, 255):
            r = self._linear_level_channel(r, self.red)

        if self.green != (0, 255):
            g = self._linear_level_channel(g, self.green)

        if self.blue != (0, 255):
            b = self._linear_level_channel(b, self.blue)

        # Put image back together
        rgb = cv2.merge((r, g, b))
        return Image.fromarray(rgb)


@dataclass
class AutoColorLevel(ImageFilter):
    threshold: int = 0

    def _compute_range(self, values):
        hist, _ = numpy.histogram(values, bins=256)
        return (
            (hist < self.threshold).sum(),
            (hist > (255 - self.threshold)).sum(),
        )

    @staticmethod
    def _linear_level_channel(values, scale):
        floor, ceil = scale
        slope = 255 / (ceil - floor)
        offset = floor * 255 / (floor - ceil)
        return numpy.maximum(0, numpy.minimum(255 , values * slope + offset)).astype(numpy.uint8)

    def process(self, image):
        rgb = numpy.asarray(image, numpy.uint8)
        r, g, b = cv2.split(rgb)

        scales = (
            self._compute_range(r),
            self._compute_range(g),
            self._compute_range(b),
        )

        r = self._linear_level_channel(r, scales[0])
        g = self._linear_level_channel(g, scales[1])
        b = self._linear_level_channel(b, scales[2])

        # Put image back together
        rgb = cv2.merge((r, g, b))
        return Image.fromarray(rgb)


@dataclass
class MirrorImage(ImageFilter):
    def process(self, image):
        return image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
