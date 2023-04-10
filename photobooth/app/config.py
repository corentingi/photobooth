from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
import yaml

from photobooth.app.entities import PhotoMontageType


def _merge_dicts(target, source):
    for key, value in source.items():
        if isinstance(target.get(key), dict):
            _merge_dicts(target[key], value)
        else:
            target[key] = value


class ConfigFromFile(BaseModel):
    @classmethod
    def load(cls):
        config_files = [
            Path("photobooth/app/configs/config_default.yml"),
            Path("photobooth/app/configs/config.yml"),
        ]

        config = {}
        for config_file in config_files:
            if not config_file.is_file():
                continue
            with open(config_file) as fh:
                _merge_dicts(
                    config,
                    yaml.load(fh, Loader=yaml.FullLoader),
                )

        return cls.parse_obj(config)


class CameraConfig(BaseModel):
    delay: int = 3
    output_directory: Path = Path("/tmp/photobooth/captures")


class FilterConfig(BaseModel):
    name: str
    params: Dict[str, Any] = {}


class ProcessingConfig(BaseModel):
    class BackgroundConfig(BaseModel):
        color: str = "white"

    class CaptureConfig(BaseModel):
        correct_orientation: bool = False
        filters: List[FilterConfig] = []
        margin: int = 5

    class TitleConfig(BaseModel):
        image_path: Optional[Path]
        filters: List[FilterConfig] = []

    template: PhotoMontageType = PhotoMontageType.STRIP_WITH_TITLE
    background: BackgroundConfig
    captures: CaptureConfig
    title: TitleConfig
    output_directory: Path = Path("/tmp/photobooth/processed")


class GpioConfig(BaseModel):
    button: int = 17
    led: int = 27


class PhotoBoothConfig(ConfigFromFile):
    camera: CameraConfig
    processing: ProcessingConfig
    gpio: GpioConfig
