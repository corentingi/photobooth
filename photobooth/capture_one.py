import platform
import subprocess

from app.capture import capture_image

if __name__ == "__main__":
    local_path = capture_image()
    print(local_path)

    if platform.system() == 'Linux':
        subprocess.call(['xdg-open', local_path])
    if platform.system() == 'Darwin':
        subprocess.call(['open', local_path])
