import re
import time
import random

from urllib.parse import urlparse
from http import HTTPMethod, HTTPStatus

from http.server import BaseHTTPRequestHandler
from mini_mock_server.http_server.response import Response
from mini_mock_server.schemas import ResponseSchema, RouteSchema


class Request:

    _response: Response
    _routes: list[RouteSchema]
    _server: BaseHTTPRequestHandler

    def __init__(self, server: BaseHTTPRequestHandler, routes: list[RouteSchema]) -> None:
        self._server = server
        self._routes = routes

        self._response = Response(server)

    def handle(self, method: HTTPMethod):
        parser = urlparse(self._server.path)

        path = parser.path

        for route in self._routes:
            path_pattern = re.sub(r":\w+", r"[\\wÀ-ÖØ-öø-ÿ_\-%$#&()@*]+", route["url"])

            match = re.fullmatch(path_pattern, path)

            if not match:
                continue

            if route["method"].upper() != method.value:
                continue

            self._apply_functionality(route)

            return

        self._response.set_error(HTTPStatus.NOT_FOUND)

    def _get_response(self, route: RouteSchema) -> ResponseSchema:
        response: ResponseSchema = route["response"]

        if isinstance(response, list):
            return random.choice(response)

        return response

    def _apply_functionality(self, route: RouteSchema):
        response = self._get_response(route)

        sleep = response.get("sleep")

        if sleep:
            time.sleep(sleep)

        self._response.set_success(response)
