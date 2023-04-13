import enum


class PictureOrientation(enum.Enum):
    PORTRAIT = "PORTRAIT"
    LANDSCAPE = "LANDSCAPE"


class PictureFormat(enum.Enum):
    FORMAT_LANDSCAPE_15x5 = (15, 5)
    FORMAT_LANDSCAPE_15x10 = (15, 10)
    FORMAT_LANDSCAPE_4x3 = (4, 3)
    FORMAT_LANDSCAPE_3x2 = (3, 2)
    FORMAT_PORTRAIT_3x4 = (3, 4)
