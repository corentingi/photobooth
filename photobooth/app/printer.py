import platform
from pathlib import Path
import subprocess

from app.config import PrintingConfig
from app.entities import PictureFormat

def print_image(
    image_path: Path,
    format: PictureFormat,
    settings: PrintingConfig,
):
    os_name = platform.system()

    command = None
    options = []
    if os_name in ["Linux", "Darwin"]:
        command = "lp"
        if settings.copies and settings.copies > 1:
            options.append("-n")
            options.append(settings.copies)
        if settings.destination:
            options.append("-d")
            options.append(settings.destination)
    else:
        raise OSError("Unsupported operating system: %s" % os_name)

    subprocess.call([command, *options, image_path])
