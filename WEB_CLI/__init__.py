from threading import Thread
from logging import getLogger
from typing import Callable, Dict, List, Optional, Union
from .helpers import UserCommand, Settings
from .server import HTMLServer
from os import path


class Server():
    def __init__(self, settings: Settings, backend: Callable[[UserCommand], None], title: str = "Server") -> None:
        self.settings = settings
        self.app = HTMLServer(self.settings.host, self.settings.port, root_path=path.dirname(__file__), _title = title)
        self.history: Dict[UserCommand, List[str]] = {}
        self.app.add_url_rule("/", self.index)
        self.app.add_url_rule("/ping/", self.ping)
        self.app.add_url_rule("/fetch", self.fetch)
        self.app.add_url_rule("/getHistory", self.get_history)
        self.app.add_url_rule("/send", self.send, "PUT")
        self.backend = backend
        self.server_thread: Thread = None

    def index(self, _):
        return self.app.render_template_file("index.html", page_title=self.settings.name)

    def get_history(self, args: Dict[str, str]):
        index = int(args["index"])
        return list(self.history.keys())[index].command

    def push_data(self, command: Optional[UserCommand], response: Union[str, List[str]]) -> None:
        if (command is None):
            command = list(self.history)[-1]
        if (isinstance(response, str)):
            self.history[command].append(response)
        else:
            self.history[command].extend(response)

    def send(self, data: bytes):
        data = UserCommand(data.decode())
        self.history[data] = []
        self.backend(data)
        return "Finished"

    def fetch(self, _):
        return [{"command": key.command, "hash": key.__hash__(), "response": value} for key, value in self.history.items()]

    def ping(self, _):
        return "Working"

    def start(self) -> None:
        self.server_thread = Thread(target=self.app.start)
        self.server_thread.start()

    def stop(self) -> None:
        raise self.app.stop()
