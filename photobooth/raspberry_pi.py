from signal import pause

from app.config import PhotoBoothConfig
from machine import RaspberryPiPhotoBooth


if __name__ == "__main__":
    photo_booth = RaspberryPiPhotoBooth(config=PhotoBoothConfig())
    print('Ready. To start taking pictures, press on the button')
    pause()
