import asyncio
from pathlib import Path
from signal import pause
from time import sleep

from gpiozero import LED, Button

from camera import Camera
from capture import capture_multiple_photos
from machine import PhotoBoothMachine


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
        print("Processing image")
        sleep(0.5)
        print("Saved processed image")
        self.processed(processed_image=Path("/tmp/processed_image.jpeg"))

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
