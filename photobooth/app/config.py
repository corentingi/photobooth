from pathlib import Path
import yaml


def _merge_dicts(target, source):
    for key, value in source.items():
        if isinstance(target.get(key), dict):
            _merge_dicts(target[key], value)
        else:
            target[key] = value


class Config():
    _config = {}

    def __init__(self):
        config_files = [
            "photobooth/app/configs/config_default.yml",
            "photobooth/app/configs/config.yml",
        ]

        for config_file in config_files:
            self._load_file(Path(config_file))

    def _load_file(self, file_name: Path):
        if not file_name.is_file():
            return

        with open(file_name) as fh:
            config = yaml.load(fh, Loader=yaml.FullLoader)

        _merge_dicts(self._config, config)

    def get(self, path, default=None):
        config = self._config
        for part in path.split("."):
            if part not in config:
                return default
            config = config[part]
        return config
