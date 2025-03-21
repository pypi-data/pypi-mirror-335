from typing import Optional, TypedDict


class ResponseSchema(TypedDict):
    sleep: Optional[int]
    status_code: int
    headers: Optional[dict]
    body: dict | list


class RouteSchema(TypedDict):
    url: str
    method: str
    response: ResponseSchema | list[ResponseSchema]
