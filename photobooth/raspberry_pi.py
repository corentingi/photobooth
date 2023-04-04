import asyncio
import logging
from gpiozero import LED, Button
from signal import pause

from capture import Camera

WAIT_BETWEEN_PHOTOS = 3

button = Button(pin=17)
led = LED(pin=27)


async def blink_led_and_wait() -> None:
    led.blink(on_time=0.5, off_time=0.5, n=WAIT_BETWEEN_PHOTOS)
    await asyncio.sleep(WAIT_BETWEEN_PHOTOS)
    return None


async def capture_multiple_photos(count: int = 3):
    logging.info("Capturing %s photos", count)

    camera = Camera(folder='/home/corentin/photos')
    await camera.init()

    local_paths = []
    try:
        logging.info("Blinking led...")
        await blink_led_and_wait()

        for i in range(0, count):
            logging.info("Capturing photo %s...", i + 1)
            capture = await camera.capture_image()

            if i < count - 1:
                logging.info("Blinking led and saving capture %s...", i)
                _, local_path = await asyncio.gather(
                    blink_led_and_wait(),
                    camera.save(capture),
                )
            else:
                logging.info("Saving capture %s...", i + 1)
                local_path = await camera.save(capture)

            local_paths.append(local_path)
    except Exception:
        raise
    finally:
        led.off()
        await camera.exit()
    return local_paths


def on_button_pressed():
    logging.info("Button pressed")
    # Capture 3 photos
    local_paths = asyncio.run(capture_multiple_photos(count=3))
    logging.debug("Paths:", local_paths)

    # Process photos
    pass

    # Print final photo
    pass


if __name__ == "__main__":
    led.off()
    button.when_activated = on_button_pressed
    print('Ready. To start taking pictures, press on the button')
    pause()
