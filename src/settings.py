import json

from pathlib import Path
import attr

from constants import SETTINGS_KEYS

SETTINGS_PATH = "~/.codesearchrc"

default_settings = {
    "SOCKET_HOST": "127.0.0.1",
    "SOCKET_PORT": 65126,
    "EXCLUDES": [],
    "FILE_TYPES": [],
    "SIGNIFICANCE_THRESHOLD": 0,
    "WATCHED": [],
    "INDEXING_PROCESSES": 4,
}


@attr.s
class Settings:
    settings = attr.ib(default=attr.Factory(dict))

    def from_file(self, path: str):
        settings_path = Path(SETTINGS_PATH).expanduser()

        if not settings_path.exists():
            self.settings = default_settings
            return

        with open(path, "r") as settings_file:
            self.settings = json.load(settings_file)

    def __getattr__(self, key):
        if key not in SETTINGS_KEYS:
            raise KeyError(f"{key} not a valid settings property")

        return self.settings[key]


settings = Settings()

settings.from_file(Path(SETTINGS_PATH).expanduser())
