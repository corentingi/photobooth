import enum


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
