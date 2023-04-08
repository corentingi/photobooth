from pathlib import Path
from machine import PhotoBoothMachine
from time import sleep


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
            Path("/Users/cgitton/Desktop/2023-04 - Prototypage photobooth/IMG_0071.CR2"),
            Path("/Users/cgitton/Desktop/2023-04 - Prototypage photobooth/IMG_0072.CR2"),
            Path("/Users/cgitton/Desktop/2023-04 - Prototypage photobooth/IMG_0073.CR2"),
        ]
        print(captures)

        self.captured(captures=captures)

        return captures

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
    photo_booth = SimulatedPhotoBooth()
    photo_booth.registered_input(pressed=True)
    print("Finished")
