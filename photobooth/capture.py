import asyncio
from collections.abc import Callable
import logging
from pathlib import Path
from typing import List, Optional

from camera import Camera


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

    return local_path


def capture_image() -> Path:
    return asyncio.run(async_capture_image())


async def capture_multiple_photos(
    count: int = 3,
    self_timer_seconds: int = 3,
    before_timer_callback: Optional[Callable[[], None]] = None,
    exception_callback: Optional[Callable[[], None]] = None,
    camera: Optional[Camera] = None,
) -> List[Path]:
    logging.info("Capturing %s photos", count)
    if camera is None:
        camera = Camera(folder='/tmp')
    await camera.init()

    local_paths = []
    try:
        logging.info("Blinking led...")
        if before_timer_callback is not None:
            before_timer_callback()
        await asyncio.sleep(self_timer_seconds)

        for i in range(0, count):
            logging.info("Capturing photo %s...", i + 1)
            capture = await camera.capture_image()

            if i < count - 1:
                logging.info("Blinking led and saving capture %s...", i)
                if before_timer_callback is not None:
                    before_timer_callback()
                _, local_path = await asyncio.gather(
                    asyncio.sleep(self_timer_seconds),
                    camera.save(capture),
                )
            else:
                logging.info("Saving capture %s...", i + 1)
                local_path = await camera.save(capture)

            local_paths.append(local_path)
    except Exception:
        raise
    finally:
        if exception_callback is not None:
            exception_callback()
        await camera.exit()
    return local_paths
