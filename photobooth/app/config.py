from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel
import yaml


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
            Path("photobooth/app/configs/default.yml"),
            Path("photobooth/app/configs/presets.yml"),
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
    count: Union[str, int] = "template"
    delay: int = 3
    output_directory: Path = Path("/tmp/photobooth/captures")


class FilterConfig(BaseModel):
    name: str
    params: Dict[str, Any] = {}


class TemplateConfig(BaseModel):
    name: str
    params: Dict[str, Any] = {}


class PresetConfig(BaseModel):
    template: TemplateConfig
    filters: List[FilterConfig] = []
    title_filters: List[FilterConfig] = []


class ProcessingConfig(BaseModel):
    class BackgroundConfig(BaseModel):
        color: str = "white"

    class TitleConfig(BaseModel):
        image_path: Optional[Path]
        filters: List[FilterConfig] = []

    preset: Optional[str] = None
    template: Optional[TemplateConfig] = None
    filters: Optional[List[FilterConfig]] = []
    title: TitleConfig
    correct_orientation: bool = False
    output_directory: Path = Path("/tmp/photobooth/processed")
    output_format: str = "jpg"


class GpioConfig(BaseModel):
    button: int = 17
    led: int = 27


class PrintingConfig(BaseModel):
    enabled: bool = False
    copies: int = 1
    delay: int = 0
    destination: Optional[str] = None


class PhotoBoothConfig(ConfigFromFile):
    camera: CameraConfig
    processing: ProcessingConfig
    gpio: GpioConfig
    printing: PrintingConfig
    presets: Dict[str, PresetConfig]
