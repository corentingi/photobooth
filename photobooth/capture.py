import asyncio
import locale
import logging
import os
from pathlib import Path

import gphoto2 as gp


class Camera():
    camera = None
    folder: str

    def __init__(self, folder='/tmp') -> None:
        locale.setlocale(locale.LC_ALL, '')
        logging.basicConfig(
            format='%(levelname)s: %(name)s: %(message)s',
            level=logging.WARNING,
        )
        self.folder = folder

    async def init(self):
        if self.camera is not None:
            return
        callback_obj = gp.check_result(gp.use_python_logging())
        self.camera = gp.Camera()
        self.camera.init()

    async def exit(self):
        if self.camera is None:
            return
        self.camera.exit()

    async def capture_image(self):
        print('Capturing image')
        return self.camera.capture(gp.GP_CAPTURE_IMAGE)

    async def save(self, capture):
        print('Camera file path: {0}/{1}'.format(capture.folder, capture.name))
        target_path = os.path.join(self.folder, capture.name)

        print('Copying image to', target_path)
        camera_file = self.camera.file_get(
            capture.folder,
            capture.name,
            gp.GP_FILE_TYPE_NORMAL
        )

        camera_file.save(target_path)


async def async_capture_image() -> Path:
    camera = Camera()
    await camera.init()
    try:
        capture = await camera.capture_image()
        local_path = await camera.save(capture)
    except Exception:
        raise
    finally:
        await camera.exit()

    return Path(local_path)


def capture_image() -> Path:
    return asyncio.run(async_capture_image())