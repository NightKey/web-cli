from dataclasses import dataclass, field
from datetime import datetime
import json
from os import path
from typing import Union


@dataclass(frozen=True, eq=True, order=True)
class UserCommand:
    command: str
    create_date: datetime = field(default_factory=datetime.now)


class Settings:
    DEFAULT_SETTINGS_FILE_NAME = "web-cli_settings.conf"

    def __init__(self, host: str = "127.0.0.1", port: int = 8080, name: str = "Web CLI"):
        self.host = host
        self.port = port
        self.name = name

    def to_file(self, string_path: str = DEFAULT_SETTINGS_FILE_NAME) -> None:
        with open(string_path, "w") as fp:
            json.dump(self.__dict__, fp)

    @staticmethod
    def from_file(string_path: str = DEFAULT_SETTINGS_FILE_NAME) -> Union["Settings", None]:
        if (not path.exists(string_path)):
            return None
        with open(string_path, "r") as fp:
            data = json.load(fp)
            return Settings(data["host"], data["port"], data["name"])
