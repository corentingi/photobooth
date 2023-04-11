import asyncio
from pathlib import Path
import time

from gpiozero import LED, Button

from app.camera import Camera
from app.capture import capture_multiple_photos
from app.machine import PhotoBoothMachine
from app.process import CaptureProcessor
from app.config import PhotoBoothConfig


class GenericPhotoBooth(PhotoBoothMachine):
    def __init__(self, config: PhotoBoothConfig):
        super().__init__()
        self.config = config
        self.camera = Camera(folder=config.camera.output_directory)

    def _before_timer_callback(self):
        pass

    def _exception_callback(self):
        pass

    def on_enter_initialization(self):
        self.initialized()

    def on_enter_capturing(self):
        captures = asyncio.run(
            capture_multiple_photos(
                count=3,
                self_timer_seconds=self.config.camera.delay,
                before_timer_callback=self._before_timer_callback,
                exception_callback=self._exception_callback,
                camera=self.camera,
            )
        )
        self.captured(captures=captures)

    def on_enter_processing(self):
        file_name = Path("%s.%s" % (
            int(time.time()),
            self.config.processing.output_format,
        ))
        file_path = self.config.processing.output_directory / file_name
        processor = CaptureProcessor(settings=self.config.processing)
        processor.process(
            captures=self.images_to_process,
            output_file_path=file_path,
        )
        self.processed(processed_image=file_path)

    def on_enter_printing(self):
        print("Printing processed image")
        time.sleep(0.5)
        print("Printed")
        self.printed()


class RaspberryPiPhotoBooth(GenericPhotoBooth):
    def __init__(self, config: PhotoBoothConfig):
        super().__init__(config=config)
        self.button = Button(led=config.gpio.button)
        self.led = LED(led=config.gpio.led)

    def _before_timer_callback(self):
        self.led.blink(on_time=0.5, off_time=0.5, n=self.config.camera.delay)

    def _exception_callback(self):
        self.led.off()

    def on_enter_initialization(self):
        self.button.when_activated = self.registered_input(pressed=True)
        self.led.blink(on_time=0.2, off_time=0.2, n=3)
        self.initialized()
