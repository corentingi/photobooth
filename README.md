# Photo Booth

## Setup

Install gphoto2 before anything else :
```bash
# Ubuntu / Debian
apt install gphoto2

# MacOS
brew install gphoto2
```

Install python dependencies
```bash
poetry install
```

## Usage

To test capturing one picture use the following command:
```bash
poetry run python photobooth/capture_one.py
```

To start the raspberry pi process:
```bash
poetry run python photobooth/raspberry_pi.py
```

## Warning

On the reaspberry pi, when gphoto2 and libgphoto2 are installed/compiled, 2 processes will be running:
```bash
$ ps -ef | grep gphoto
user   885   611  0 18:05 ?        00:00:00 /usr/libexec/gvfs-gphoto2-volume-monitor
user  1027   725  0 18:05 ?        00:00:00 /usr/libexec/gvfsd-gphoto2 --spawner :1.7 /org/gtk/gvfs/exec_spaw/1
```

Those need to be killed before you can connect to the device with gphoto2.

For the moment the quick solution is to kill them:

```bash
sudo rm -rf /usr/libexec/gvfs-gphoto2-volume-monitor /usr/libexec/gvfsd-gphoto2
```
