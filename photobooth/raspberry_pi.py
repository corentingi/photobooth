from gpiozero import LED, Button
from signal import pause
from time import sleep

from capture import capture_image

WAIT_BETWEEN_PHOTOS = 3

button = Button(pin=2)
leds = [
    LED(pin=17),
    LED(pin=27),
    LED(pin=22),
]


def setup():
    for led in leds:
        led.off()


def capture_3_photos():
    paths = []
    for i in range(0, 3):
        leds[i].blink(on_time=0.5, off_time=0.5, n=WAIT_BETWEEN_PHOTOS)
        sleep(WAIT_BETWEEN_PHOTOS)  # Wait X seconds
        leds[i].on()

        local_path = capture_image()
        paths.append(local_path)

    for led in leds:
        led.off()

    print(paths)


if __name__ == "__main__":
    setup()
    button.when_activated = capture_3_photos
    print('Ready. To start taking pictures, press on the button')
    pause()
