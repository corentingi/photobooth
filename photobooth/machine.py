import asyncio
import logging
import os
from pathlib import Path
import time

from gpiozero import LED, Button

from app.camera import Camera
from app.capture import capture_multiple_photos
from app.machine import PhotoBoothMachine
from app.process import CaptureProcessor
from app.config import PhotoBoothConfig
from app.printer import print_image


class GenericPhotoBooth(PhotoBoothMachine):
    def __init__(self, config: PhotoBoothConfig):
        super().__init__()
        self.config = config
        self.camera = Camera(folder=config.camera.output_directory)
        self.processor = CaptureProcessor(
            settings=self.config.processing,
            presets=self.config.presets,
        )

        # Prepare output directories
        os.makedirs(self.config.camera.output_directory, exist_ok=True)
        os.makedirs(self.config.processing.tmp_directory, exist_ok=True)
        os.makedirs(self.config.processing.output_directory, exist_ok=True)

    def _before_timer_callback(self):
        pass

    def _exception_callback(self):
        pass

    def _printing_callback(self):
        pass

    def on_enter_initialization(self):
        self.initialized()

    def on_enter_capturing(self):
        capture_count = self.config.camera.count
        if capture_count == "template":
            capture_count = self.processor.template.capture_count

        try:
            captures = asyncio.run(
                capture_multiple_photos(
                    count=capture_count,
                    self_timer_seconds=self.config.camera.delay,
                    before_timer_callback=self._before_timer_callback,
                    exception_callback=self._exception_callback,
                    camera=self.camera,
                )
            )
        except Exception as e:
            logging.error(e)
            self.failed()
        else:
            self.captured(captures=captures)

    def on_enter_processing(self):
        file_name = Path("%s.%s" % (
            int(time.time()),
            self.config.processing.output_format,
        ))
        tmp_file_path = self.config.processing.tmp_directory / file_name
        self.processor.process(
            captures=self.images_to_process,
            output_file_path=tmp_file_path,
        )
        file_path = self.config.processing.output_directory / file_name
        os.rename(tmp_file_path, file_path)
        self.processed(processed_image=file_path)

    def on_enter_printing(self):
        print("Printing processed image...")
        if self.config.printing.enabled:
            print_image(
                self.image_to_print,
                format=self.processor.template.format,
                settings=self.config.printing,
            )
        else:
            print("Skipped")
        self._printing_callback()
        time.sleep(self.config.printing.delay)
        self.printed()


class RaspberryPiPhotoBooth(GenericPhotoBooth):
    def __init__(self, config: PhotoBoothConfig):
        self.button = Button(pin=config.gpio.button)
        self.led = LED(pin=config.gpio.led)
        super().__init__(config=config)

    def _before_timer_callback(self):
        self.led.blink(on_time=0.5, off_time=0.5, n=self.config.camera.delay)

    def _exception_callback(self):
        self.led.off()

    def _printing_callback(self):
        if self.config.printing.delay:
            self.led.blink(on_time=0.1, off_time=0.1, n=self.config.printing.delay * 5)

    def on_enter_initialization(self):
        self.button.when_activated = lambda: self.registered_input(pressed=True)
        self.led.blink(on_time=0.2, off_time=0.2, n=3)
        self.initialized()
