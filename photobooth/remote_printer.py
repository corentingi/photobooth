import os
from pathlib import Path
import shutil
from signal import pause
import subprocess
from time import sleep
import glob

from app.config import PhotoBoothConfig
from app.printer import print_image


if __name__ == "__main__":
    config = PhotoBoothConfig.load()

    connection = "{user}@{host}".format(
        user=config.remote.user,
        host=config.remote.host,
    )
    remote_location = "{connection}:{location}".format(
        connection=connection,
        location=config.remote.remote_output_directory,
    )
    local_fetch_directory = config.remote.local_fetch_directory
    local_printed_directory = config.remote.local_printed_directory
    remote_output_directory = config.remote.remote_output_directory
    remote_printed_directory = config.remote.remote_printed_directory

    os.makedirs(local_fetch_directory, exist_ok=True)
    os.makedirs(local_printed_directory, exist_ok=True)

    print('Creating remote printed directory...')
    subprocess.call(["ssh", connection, "mkdir", "-p", str(remote_printed_directory)])

    print('Ready to start printing pictures.')
    while True:
        print("Fetching processed files...")
        subprocess.call(["rsync", "-av", "--delete", str(remote_location) + "/", str(local_fetch_directory) + "/"])

        files = glob.glob(str(local_fetch_directory / "*"))
        if files:
            print("Printing local files...")
        for file in files:
            print("Printing %s" % file)
            print_image(Path(file), format=None, settings=config.printing)
            shutil.move(file, local_printed_directory)

        if files:
            print("Moving remote files...")
            subprocess.call(["ssh", connection, "mv", str(remote_output_directory / "*"), str(remote_printed_directory)])

        print("Sleeping...")
        sleep(config.remote.delay)
