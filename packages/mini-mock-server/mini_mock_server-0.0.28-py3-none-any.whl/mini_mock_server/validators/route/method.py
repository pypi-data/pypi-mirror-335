from http import HTTPMethod

from mini_mock_server.schemas import RouteSchema


def validate(base_path: str, route: RouteSchema, route_idx: int):
    if "method" not in route:
        raise ValueError(f'"method" key is required. Route {route_idx} from "{base_path}"')

    try:
        HTTPMethod(route["method"].upper())

    except ValueError as exc:
        raise ValueError(f'{exc}. Route {route_idx} from "{base_path}"')
