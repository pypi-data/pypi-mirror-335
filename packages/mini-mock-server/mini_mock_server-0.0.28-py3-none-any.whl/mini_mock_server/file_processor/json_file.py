import os
import json

from json.decoder import JSONDecodeError
from mini_mock_server.schemas import RouteSchema
from mini_mock_server.validators.route import validator as route_validator


def read(fpath: str) -> list[RouteSchema]:
    if not fpath.endswith(".json"):
        raise ValueError("Spec file must be a .json")

    with open(fpath) as file:
        try:
            raw_spec = json.load(file)
        except JSONDecodeError as exc:
            _, target = str(exc).split(":")

            target = target.strip()

            raise ValueError(f"Invalid json file, error on {target}")

    return _build_routes(raw_spec)


def _normalize_route(base_path: str, raw_route: RouteSchema) -> RouteSchema:
    route = {**raw_route}

    url = route["url"].lstrip("/")

    path = base_path

    if url != "":
        path = os.path.join(base_path, url)

    if not path.startswith("/"):
        path = f"/{path}"

    route["url"] = path

    return route


def _route_id(route: RouteSchema):
    return f'{route["method"].lower()}_{route["url"]}'


def _build_routes(json_routes: dict[str, list[RouteSchema]]) -> list[RouteSchema]:
    built_routes = {}

    for base_path, routes in json_routes.items():

        if not isinstance(routes, list):
            raise ValueError("Routes must be a list")

        for i, raw_route in enumerate(routes, start=1):
            route_validator.validate(base_path, raw_route, i)

            route = _normalize_route(base_path, raw_route)

            route_id = _route_id(route)

            if route_id in built_routes:
                raise ValueError(f"You can't define duplicated routes: {route['url']}")

            built_routes[route_id] = route

    return list(built_routes.values())
