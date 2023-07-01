from typing import Callable, Dict, Optional, Union, Any, List
from os import path
from smdb_logger import Logger, LEVEL
import http.server
import socketserver


from threading import Thread
from time import sleep, perf_counter_ns

class ResponseCode():
    def __init__(self, value: int, name: str):
        self.value = value
        self.name = name

    def __str__(self) -> str:
        return f"{self.value} {self.name}"
    
class Timer():
    def __init__(self):
        self.start = perf_counter_ns()
        self.end = 0
    
    def stop(self):
        self.end = perf_counter_ns()

    def __str__(self) -> str:
        return f"{(self.end - self.start)/1000000}"

NotFound = ResponseCode(404, "NOt Found")
Ok = ResponseCode(200, "Ok")
InternalServerError = ResponseCode(500, "Internal Server Error")
TPot = ResponseCode(418, "I'm a teapot")

get_rules: Dict[str, Callable[[Dict[str, str]], None]] = {}
put_rules: Dict[str, Callable[[bytes], None]] = {}
title: str = None
html_template: str = "<html><header><link rel='stylesheet' href='/static/style.css' /><title>{title}</title></header><body>{content}</body></html>"
http_header: str = "HTTP/1.0 {response_code}\nContent-Length: {length}\nContent-Type: {content_type};\nServer-Timing: {timing}\nKeep-Alive: timeout=100, max=1000\r\n\r\n{payload}"
cwd: str = "."

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __404__(self, do_get: Timer) -> None:
        _404_time = Timer()
        _404_file = html_template.format(title=title, content="404 NOT FOUND")
        _404_time.stop()
        do_get.stop()
        self.send_message(NotFound, _404_file, f"full;dur={do_get}, process;dur={_404_time}")

    @staticmethod
    def render_static_file(cwd: str, name: str) -> str:
        with open(path.join(cwd, HTMLServer.STATIC_FOLDER, name), "r") as fp:
            return fp.read(-1)

    def send_message(self, response_code: ResponseCode, payload: Union[str, Dict[Any, Any], List[Any]], timing: str = "") -> None:
        content_type = "text/html"
        if isinstance(payload, (dict, list)):
            content_type = "application/json"
        header = http_header.format(response_code=response_code, content_type=content_type, length=len(str(payload)), payload=payload, timing=timing).encode()
        self.wfile.write(header)

    def do_GET(self) -> None:
        do_get = Timer()
        if (self.path in get_rules.keys()):
            get_rules_time = Timer()
            path_params = {item.split("=")[0]: item.split("=")[1] for item in self.path.split("?")[-1].split("&") if len(item.split("=")) == 2}
            html_file = ""
            response_code: ResponseCode = None
            try:
                html_file = get_rules[self.path](path_params)
                response_code = Ok
            except Exception as ex:
                html_file = html_template.format(title=title, content=ex)
                response_code = InternalServerError
            finally:
                do_get.stop()
                get_rules_time.stop()
                self.send_message(response_code, html_file, f"full;dur={do_get}, process;dur={get_rules_time}")
                return
        if self.path.startswith("/static"):
            static = Timer()
            html_file = HTTPRequestHandler.render_static_file(cwd, self.path.split("/")[-1])
            static.stop()
            do_get.stop()
            self.send_message(Ok, html_file, f"full;dur={do_get}, process;dur={static}")
            return
        self.__404__(do_get)
    
    def do_PUT(self) -> None:
        do_put = Timer()
        if (self.path not in put_rules.keys()):
            self.__404__(do_put)
            return
        data = self.rfile.read(int(self.headers.get("Content-Length")))
        do_put.stop()
        self.send_message(Ok, "", f"full={do_put}")
        try:
            put_rules[self.path](data)
        except Exception as ex:
            self.send_message(InternalServerError, ex)

class HTMLServer:
    TEMPLATE_FOLDER = "templates"
    STATIC_FOLDER = "static"

    def __init__(self, host: str, port: int, root_path: str = ".", logger: Optional[Logger] = None, _title: str = "HTML Server"):
        global title
        global cwd
        self.host = host
        self.port = port
        self.logger = logger
        self.handler = HTTPRequestHandler
        self.httpd: socketserver.TCPServer = None
        title = _title
        cwd = root_path

    def try_log(self, data: str, log_level: LEVEL = LEVEL.INFO) -> None:
        if self.logger == None:
            return
        self.logger.log(log_level, data)

    def render_static_file(self, name: str) -> str:
        return HTTPRequestHandler.render_static_file(cwd, name)

    def render_template_file(self, name: str, **kwargs) -> str:
        data: str = ""
        with open(path.join(cwd, HTMLServer.TEMPLATE_FOLDER, name), "r") as fp:
            data = fp.read(-1)
        for template, value in kwargs.items():
            data = data.replace("{{ " + template + " }}", value)
        return data

    def add_url_rule(self, rule: str, callback: Union[Callable[[Dict[str, str]], None], Callable[[bytes], None]], protocol: str = "GET") -> None:
        if (protocol == "GET"):
            get_rules[rule] = callback
        if (protocol == "PUT"):
            put_rules[rule] = callback

    def start(self):
        self.httpd = socketserver.TCPServer(
            (self.host, self.port), self.handler)
        self.try_log(f"Started to serve on {self.host}:{self.port}")
        self.httpd.serve_forever()

    def stop(self):
        self.try_log("Stopping server")
        self.httpd.shutdown()


if __name__=="__main__":
    server = HTMLServer("localhost", 8080, root_path=path.dirname(__file__), logger=Logger("test.log", log_to_console=True))
    server_th = Thread(target=server.start)
    server_th.start()
    sleep(0.5)
    input("..")
    server.stop()
    server_th.join()
    exit(0)