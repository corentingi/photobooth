import asyncio
from gpiozero import LED, Button
from signal import pause

from capture import Camera

WAIT_BETWEEN_PHOTOS = 3

button = Button(pin=15)
led = LED(pin=14)


async def blink_led_and_wait() -> None:
    led.blink(on_time=0.5, off_time=0.5, n=WAIT_BETWEEN_PHOTOS)
    return asyncio.sleep(WAIT_BETWEEN_PHOTOS)


async def capture_3_photos():
    camera = Camera()
    await camera.init()
    local_paths = []
    try:
        await blink_led_and_wait()

        # Photo 1:
        capture = await camera.capture_image()

        local_path, _ = await asyncio.gather(
            camera.save(capture),
            blink_led_and_wait()
        )
        local_paths.append(local_path)

        # Photo 2:
        await camera.capture_image()
        local_path, _ = await asyncio.gather(
            camera.save(capture),
            blink_led_and_wait()
        )
        local_paths.append(local_path)

        # Photo 3:
        await camera.capture_image()
        local_path = await camera.save(capture)
        local_paths.append(local_path)
    except Exception:
        pass
    finally:
        led.off()
        await camera.exit()
    return local_paths


def on_button_pressed():
    # Capture 3 photos
    local_paths = asyncio.run(capture_3_photos())
    print(local_paths)

    # Process photos
    pass

    # Print final photo
    pass


if __name__ == "__main__":
    led.off()
    button.when_activated = on_button_pressed
    print('Ready. To start taking pictures, press on the button')
    pause()
