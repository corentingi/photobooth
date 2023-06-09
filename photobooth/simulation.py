from pathlib import Path
import platform
import subprocess
import time

from app.config import PhotoBoothConfig
from machine import GenericPhotoBooth


class SimulatedPhotoBooth(GenericPhotoBooth):
    def on_enter_capturing(self):
        for i in range(0, 3):
            print("Capturing fake image %s" % (i + 1))
            time.sleep(self.config.camera.delay)

        captures = [
            Path("/Users/cgitton/Desktop/photobooth/IMG_0101.tiff"),
            Path("/Users/cgitton/Desktop/photobooth/IMG_0102.tiff"),
            Path("/Users/cgitton/Desktop/photobooth/IMG_0103.tiff"),
        ]
        print(captures)
        self.captured(captures=captures)


if __name__ == "__main__":
    photo_booth = SimulatedPhotoBooth(config=PhotoBoothConfig.load())
    photo_booth.registered_input(pressed=True)

    print(photo_booth.image_to_print)

    if platform.system() == 'Linux':
        subprocess.call(['xdg-open', photo_booth.image_to_print])
    if platform.system() == 'Darwin':
        subprocess.call(['open', photo_booth.image_to_print])

    print("Finished")
