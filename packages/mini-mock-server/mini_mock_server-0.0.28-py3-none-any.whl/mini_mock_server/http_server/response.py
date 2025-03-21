import json

from http import HTTPStatus

from http.server import BaseHTTPRequestHandler

from mini_mock_server.schemas import ResponseSchema


DEFAULT_HEADER = {
    "Content-type": "application/json",
}

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
}


class Response:

    _server: BaseHTTPRequestHandler

    def __init__(self, server: BaseHTTPRequestHandler) -> None:
        self._server = server

    def set_error(self, status_code: HTTPStatus):
        self._server.send_response(status_code.value)
        headers = {**DEFAULT_HEADER, **CORS_HEADERS}

        for k, v in headers.items():
            self._server.send_header(k, v)

        self._server.end_headers()

        resp_data = self.to_json({"error": status_code.phrase})

        self._server.wfile.write(resp_data)

    def set_success(self, response: ResponseSchema):
        self._server.send_response(response["status_code"])

        headers = response.get("headers", DEFAULT_HEADER)

        headers = {**CORS_HEADERS, **headers}

        for k, v in headers.items():
            self._server.send_header(k, v)

        self._server.end_headers()

        response_data = response.get("body", {})

        self._server.wfile.write(self.to_json(response_data))

    @classmethod
    def to_json(cls, body: dict | list):
        return json.dumps(body, ensure_ascii=False).encode("utf-8")
