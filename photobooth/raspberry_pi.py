import asyncio
import os
from pathlib import Path
from signal import pause
from time import sleep, time

from gpiozero import LED, Button

from camera import Camera
from capture import capture_multiple_photos
from image_filters import BlackAndWhite, LevelImage
from machine import PhotoBoothMachine
from process import process_images


WAIT_BETWEEN_IMAGES = 3


class RaspberryPiPhotoBooth(PhotoBoothMachine):
    camera = Camera(folder='/home/corentin/photos')
    button = Button(pin=17)
    led = LED(pin=27)

    def _notify_imminent_capture(self):
        self.led.blink(on_time=0.5, off_time=0.5, n=WAIT_BETWEEN_IMAGES)

    @PhotoBoothMachine.initialization.enter
    def initialize(self):
        self.button.when_activated = self.registered_input(pressed=True)
        self.led.blink(on_time=0.2, off_time=0.2, n=3)

    @PhotoBoothMachine.capturing.enter
    def capture_images(self):
        captures = asyncio.run(
            capture_multiple_photos(
                count=3,
                self_timer_seconds=WAIT_BETWEEN_IMAGES,
                before_timer_callback=self._notify_imminent_capture,
                exception_callback=self.led.off,
                camera=self.camera,
            )
        )
        self.captured(captures=captures)

    @PhotoBoothMachine.processing.enter
    def process_images(self):
        file_name = str(int(time())) + ".jpg"
        output_image_path = Path("/home/corentin/captures") / Path(file_name)
        os.makedirs(output_image_path, exist_ok=True)
        process_images(
            captures=self.images_to_process,
            output_path=output_image_path,
            title_image=Path("/Users/cgitton/Desktop/photobooth/alo&coco.png"),
            filters=[BlackAndWhite(), LevelImage()]
        )
        self.processed(processed_image=output_image_path)

    @PhotoBoothMachine.printing.enter
    def print_processed_image(self):
        print("Printing processed image")
        sleep(0.5)
        print("Printed")
        self.printed()


if __name__ == "__main__":
    photo_booth = RaspberryPiPhotoBooth()
    print('Ready. To start taking pictures, press on the button')
    pause()
