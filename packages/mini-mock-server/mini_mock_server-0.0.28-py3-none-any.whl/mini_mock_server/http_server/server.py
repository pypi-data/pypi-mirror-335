from http import HTTPMethod

from socketserver import ForkingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler

from mini_mock_server.http_server.response import CORS_HEADERS
from mini_mock_server.schemas import RouteSchema
from mini_mock_server.http_server.request import Request
from mini_mock_server.file_processor import json_file


class ForkingHTTPServer(ForkingMixIn, HTTPServer):  # pragma: no cover
    pass


class ServerHandler(BaseHTTPRequestHandler):  # pragma: no cover
    routes: list[RouteSchema] = []

    @classmethod
    def load_file(cls, fpath: str):
        cls.routes = json_file.read(fpath)

    def __init__(self, *args, **kwargs) -> None:
        self._request = Request(self, self.routes)

        super().__init__(*args, **kwargs)

    def parse_request(self) -> None:
        super().parse_request()

        http_method = HTTPMethod(self.command)

        if http_method == HTTPMethod.OPTIONS:
            self.send_response(200, "ok")

            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)

            self.end_headers()

        else:
            self._request.handle(http_method)


def run_server(mock_fpath: str, host: str = "", port: int = 8000):
    server_address = (host, port)

    ServerHandler.load_file(mock_fpath)

    server = ForkingHTTPServer(server_address, ServerHandler)

    print(f"Mock server running on port {port}...")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
