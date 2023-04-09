import abc
from dataclasses import dataclass

import cv2
import numpy
from PIL import Image, ImageEnhance


class ImageFilter(abc.ABC):
    def process(self, image):
        pass


@dataclass
class BlackAndWhite(ImageFilter):
    def process(self, image):
        filter = ImageEnhance.Color(image)
        return filter.enhance(0)

@dataclass
class LevelImage(ImageFilter):
    level: int = 2

    def process(self, image):
        image_array = numpy.asarray(image, numpy.uint8)
        hsv = cv2.cvtColor(image_array, cv2.COLOR_RGB2HSV)
        h,s,v = cv2.split(hsv)
        floor = numpy.percentile(v, self.level) # 5% of pixels will be black
        ceil = numpy.percentile(v, 100 - self.level) # 5% of pixels will be white
        a = 255 / (ceil - floor)
        b = floor * 255 / (floor - ceil)
        v = numpy.maximum(0, numpy.minimum(255 , v * a + b)).astype(numpy.uint8)
        hsv = cv2.merge((h,s,v))
        rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)

        return Image.fromarray(rgb)
