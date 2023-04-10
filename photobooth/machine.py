import asyncio
import os
from pathlib import Path
import time
from typing import Optional

from gpiozero import LED, Button

from app import image_filters
from app.camera import Camera
from app.capture import capture_multiple_photos
from app.config import Config
from app.machine import PhotoBoothMachine
from app.process import process_images


class GenericPhotoBooth(PhotoBoothMachine):
    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.camera = Camera(folder=config.get("camera.output_directory", "/tmp/captures"))

    @property
    def _filters(self):
        return [
            getattr(image_filters, filter["name"])(**filter.get("params", {}))
            for filter in self.config.get("processing.filters", [])
        ]

    @property
    def _processed_file_name(self) -> Path:
        file_name = Path(str(int(time.time())) + ".jpg")
        directory = Path(self.config.get("processing.output_directory", "/tmp/processed"))
        os.makedirs(directory, exist_ok=True)
        return directory / file_name

    @property
    def _title_image(self) -> Optional[Path]:
        title_image = self.config.get("processing.title_image")
        if title_image:
            return Path(title_image)
        return None

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
                self_timer_seconds=self.config.get("camera.delay", 3),
                before_timer_callback=self._before_timer_callback,
                exception_callback=self._exception_callback,
                camera=self.camera,
            )
        )
        self.captured(captures=captures)

    def on_enter_processing(self):
        processed_file_name = self._processed_file_name
        process_images(
            captures=self.images_to_process,
            output_path=processed_file_name,
            title_image=self._title_image,
            filters=self._filters
        )
        self.processed(processed_image=processed_file_name)

    def on_enter_printing(self):
        print("Printing processed image")
        time.sleep(0.5)
        print("Printed")
        self.printed()


class RaspberryPiPhotoBooth(GenericPhotoBooth):
    def __init__(self, config: Config):
        super().__init__(config=config)
        self.button = Button(led=config.get("gpio.button", 17))
        self.led = LED(led=config.get("gpio.led", 27))

    def _before_timer_callback(self):
        self.led.blink(on_time=0.5, off_time=0.5, n=self.config.get("camera.delay", 3))

    def _exception_callback(self):
        self.led.off()

    def on_enter_initialization(self):
        self.button.when_activated = self.registered_input(pressed=True)
        self.led.blink(on_time=0.2, off_time=0.2, n=3)
        self.initialized()
