from signal import pause

from app.config import Config
from machine import RaspberryPiPhotoBooth


if __name__ == "__main__":
    photo_booth = RaspberryPiPhotoBooth(config=Config())
    print('Ready. To start taking pictures, press on the button')
    pause()
