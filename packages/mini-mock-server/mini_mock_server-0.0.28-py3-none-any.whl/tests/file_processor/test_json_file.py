import json
import pytest

from pathlib import Path
from http import HTTPStatus

from mini_mock_server.schemas import RouteSchema
from mini_mock_server.file_processor import json_file


def test_build_routes():
    inpt: dict[str, list[RouteSchema]] = {
        "/api": [
            {
                "url": "/users",
                "method": "GET",
                "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
            },
            {
                "url": "/products",
                "method": "GET",
                "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
            },
        ]
    }

    expected = [
        {
            "url": "/api/users",
            "method": "GET",
            "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
        },
        {
            "url": "/api/products",
            "method": "GET",
            "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
        },
    ]

    assert json_file._build_routes(inpt) == expected


def test_build_routes_fail_duplicated_route():
    inpt: dict[str, list[RouteSchema]] = {
        "/api": [
            {
                "url": "/users",
                "method": "GET",
                "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
            },
            {
                "url": "/users",
                "method": "GET",
                "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
            },
        ]
    }

    with pytest.raises(ValueError) as exc:
        json_file._build_routes(inpt)

    assert "You can't define duplicated routes" in str(exc.value)


def test_build_routes_fail_routes_isnt_a_list():
    inpt: dict[str, list[RouteSchema]] = {
        "/api": {
            "url": "/users",
            "method": "GET",
            "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
        }
    }

    with pytest.raises(ValueError) as exc:
        json_file._build_routes(inpt)

    assert "Routes must be a list" in str(exc.value)


def test_read(tmp_path: Path):
    route = {
        "api": [{"url": "/fake", "method": "GET", "response": {"status_code": HTTPStatus.OK.value}}]
    }
    expected = [
        {"url": "/api/fake", "method": "GET", "response": {"status_code": HTTPStatus.OK.value}}
    ]

    file = tmp_path / "fake.json"

    file.write_text(json.dumps(route))

    assert json_file.read(str(file)) == expected


def test_read_fail():
    with pytest.raises(ValueError):
        assert json_file.read("fake.txt")


def test_read_fail_invalid_json(tmp_path: Path):
    file = tmp_path / "fake.json"

    file.write_text('{"test": "test",}')

    with pytest.raises(ValueError) as exc:
        assert json_file.read(str(file))

    assert "on line 1 column 17" in str(exc.value)
