from threading import Thread
from smdb_logger import Logger
from typing import Callable, Dict, List, Optional, Union
from .helpers import UserCommand, Settings
from .server import HTMLServer
from os import path


class WebCLIServer():
    def __init__(self, settings: Settings, backend: Callable[[UserCommand], None], logger: Optional[Logger] = None) -> None:
        self.settings = settings
        self.app = HTMLServer(self.settings.host, self.settings.port, root_path=path.dirname(__file__), logger=logger, _title=self.settings.name)
        self.history: Dict[UserCommand, List[str]] = {}
        self.app.add_url_rule("/", self.__index)
        self.app.add_url_rule("/ping/", self.__ping)
        self.app.add_url_rule("/fetch", self.__fetch)
        self.app.add_url_rule("/getHistory", self.__get_history)
        self.app.add_url_rule("/send", self.__send, "PUT")
        self.backend = backend
        self.server_thread: Thread = None

    def __index(self, _):
        return self.app.render_template_file("index.html", page_title=self.settings.name)

    def __get_history(self, args: Dict[str, str]):
        index = int(args["index"])
        return list(self.history.keys())[index].command

    def push_data(self, response: Union[str, List[str]], command: Optional[UserCommand] = None) -> None:
        if (command is None):
            if len(self.history.keys()) < 1:
                self.history[UserCommand("")] = []
            command = list(self.history.keys())[-1]
        if (isinstance(response, str)):
            self.history[command].append(response)
        else:
            self.history[command].extend(response)

    def __send(self, data: bytes):
        data = UserCommand(data.decode())
        self.history[data] = []
        self.backend(data)
        return "Finished"

    def __fetch(self, _):
        return {"payload": [{"command": key.command, "hash": key.__hash__(), "response": value} for key, value in self.history.items()]}

    def __ping(self, _):
        return "Working"

    def start(self) -> None:
        self.server_thread = Thread(target=self.app.serve_forever)
        self.server_thread.start()

    def stop(self) -> None:
        self.app.stop()
