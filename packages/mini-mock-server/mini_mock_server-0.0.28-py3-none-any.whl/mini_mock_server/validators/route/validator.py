from mini_mock_server.schemas import RouteSchema
from mini_mock_server.validators.route import method as method_validator
from mini_mock_server.validators.route import response as response_validator


def validate(base_path: str, route: RouteSchema, route_idx: int):
    if not isinstance(route, dict):
        raise ValueError("Route must be an object")

    if "url" not in route:
        raise ValueError(f'"url" key is required. Route {route_idx} from "{base_path}"')

    method_validator.validate(base_path, route, route_idx)

    response_validator.validate(base_path, route, route_idx)
