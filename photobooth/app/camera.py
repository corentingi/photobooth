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

        # Prepare location
        os.makedirs(self.folder, exist_ok=True)

    async def exit(self):
        if self.camera is None:
            return
        self.camera.exit()

    async def capture_image(self):
        logging.debug('Capturing image')
        return self.camera.capture(gp.GP_CAPTURE_IMAGE)

    async def save(self, capture) -> Path:
        logging.debug('Camera file path: {0}/{1}'.format(capture.folder, capture.name))
        target_path = os.path.join(self.folder, capture.name)

        logging.debug('Copying image to', target_path)
        camera_file = self.camera.file_get(
            capture.folder,
            capture.name,
            gp.GP_FILE_TYPE_NORMAL,
        )

        camera_file.save(target_path)
        return Path(target_path)
