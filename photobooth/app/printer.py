import platform
from pathlib import Path
import subprocess

from app.entities import PictureFormat

def print_image(image_path: Path, format: PictureFormat, copies: int = 1):
    os_name = platform.system()

    command = None
    options = []
    if os_name in ["Linux", "Darwin"]:
        command = "lp"
        if copies:
            options.append("-n %s" % copies)
    else:
        raise OSError("Unsupported operating system: %s" % os_name)

    subprocess.call([command, *options, image_path])
