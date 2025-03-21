from typing import Optional
from http import HTTPStatus

from mini_mock_server.schemas import ResponseSchema, RouteSchema


def validate(base_path: str, route: RouteSchema, route_idx: int):
    if "response" not in route:
        raise ValueError(f'"response" key is required. Route {route_idx} from "{base_path}"')

    responses: ResponseSchema = route.get("response", {})

    if isinstance(responses, list):
        if len(responses) == 0:
            raise ValueError(f'"response" can\'t be empty. Route {route_idx} from "{base_path}"')

        for ridx, response in enumerate(responses):
            _validate_response_item(response, route_idx, base_path, ridx)

    elif isinstance(responses, dict):
        _validate_response_item(responses, route_idx, base_path)

    else:
        raise ValueError(
            f'"response" key must be a list of object or an object. Route {route_idx} from "{base_path}"'
        )


def _validate_response_status_code(
    response: ResponseSchema, route_idx: int, base_path: str, str_idx: str
):
    if "status_code" not in response:
        raise ValueError(
            f'"response{str_idx}.status_code" key is required. Route {route_idx} from "{base_path}"'
        )

    try:
        HTTPStatus(response["status_code"])

    except ValueError as exc:
        raise ValueError(f'{exc}. Route {route_idx} from "{base_path}"')


def _validate_response_item(
    response: ResponseSchema, route_idx: int, base_path: str, resp_idx: Optional[int] = None
):
    str_idx = ""

    if resp_idx is not None:
        str_idx = f"[{resp_idx}]"

    sleep = response.get("sleep")

    if sleep and not isinstance(sleep, int):
        raise ValueError(
            f'"response{str_idx}.sleep" must be an int. Route {route_idx} from "{base_path}"'
        )

    _validate_response_status_code(response, route_idx, base_path, str_idx)

    _validate_headers(response, route_idx, base_path, str_idx)


def _validate_headers(response: ResponseSchema, route_idx: int, base_path: str, str_idx: str):
    headers = response.get("headers")

    if headers is not None and not isinstance(headers, dict):
        raise ValueError(
            f'"response{str_idx}.headers" must be an object. Route {route_idx} from "{base_path}"'
        )
