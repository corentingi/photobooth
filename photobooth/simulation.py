from pathlib import Path
from machine import PhotoBoothMachine
from time import sleep

from image_filters import BlackAndWhite, LevelImage
from process import process_images


class SimulatedPhotoBooth(PhotoBoothMachine):
    @PhotoBoothMachine.initialization.enter
    def initialize(self):
        self.initialized()

    @PhotoBoothMachine.capturing.enter
    def capture_images(self):
        for i in range(0, 3):
            print("Capturing image %s" % (i + 1))
            sleep(0.5)

        captures = [
            Path("/Users/cgitton/Desktop/photobooth/IMG_0101.CR2"),
            Path("/Users/cgitton/Desktop/photobooth/IMG_0102.CR2"),
            Path("/Users/cgitton/Desktop/photobooth/IMG_0103.CR2"),
        ]
        print(captures)
        self.captured(captures=captures)

    @PhotoBoothMachine.processing.enter
    def process_captures(self):
        print("Processing image")
        output_image_path = Path("/Users/cgitton/Downloads/montage.jpg")
        process_images(
            captures=self.images_to_process,
            output_path=output_image_path,
            title_image=Path("/Users/cgitton/Desktop/photobooth/alo&coco.png"),
            filters=[BlackAndWhite(), LevelImage()]
        )
        print("Saved processed image")
        self.processed(processed_image=output_image_path)

    @PhotoBoothMachine.printing.enter
    def print_processed_image(self):
        print("Printing processed image")
        print(self.image_to_print)
        sleep(0.5)
        print("Printed")
        self.printed()


if __name__ == "__main__":
    photo_booth = SimulatedPhotoBooth()
    photo_booth.registered_input(pressed=True)
    print("Finished")
