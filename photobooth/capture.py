import locale
import logging
import os
from pathlib import Path

import gphoto2 as gp


def _gphoto2_capture_image() -> str:
    locale.setlocale(locale.LC_ALL, '')
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s',
        level=logging.WARNING,
    )

    print('Init camera')
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()

    try:
        print('Capturing image')
        file_path = camera.capture(gp.GP_CAPTURE_IMAGE)

        print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
        target = os.path.join('/tmp', file_path.name)

        print('Copying image to', target)
        camera_file = camera.file_get(
            file_path.folder,
            file_path.name,
            gp.GP_FILE_TYPE_NORMAL
        )

        camera_file.save(target)
    except Exception:
        raise
    finally:
        camera.exit()

    return target


def capture_image() -> Path:
    local_path = _gphoto2_capture_image()
    return Path(local_path)
