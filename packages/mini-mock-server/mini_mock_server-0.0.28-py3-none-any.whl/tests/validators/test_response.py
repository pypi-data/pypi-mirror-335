import pytest

from http import HTTPMethod, HTTPStatus

from mini_mock_server.validators.route import validator as route_validator


def test_route_validator_no_response():
    route_spec = {"url": "/users", "method": HTTPMethod.GET.value}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"response" key is required' in str(exc.value)


def test_route_validator_invalid_response():
    route_spec = {"url": "/users", "method": HTTPMethod.GET.value, "response": ""}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"response" key must be a list of object or an object' in str(exc.value)


def test_route_validator_no_response_status_code():
    route_spec = {"url": "/users", "method": HTTPMethod.GET.value, "response": {}}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"response.status_code" key is required' in str(exc.value)


def test_route_validator_no_responses_status_code():
    route_spec = {"url": "/users", "method": HTTPMethod.GET.value, "response": [{}]}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"response[0].status_code" key is required' in str(exc.value)


def test_route_validator_empty_responses_status_code():
    route_spec = {"url": "/users", "method": HTTPMethod.GET.value, "response": []}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"response" can\'t be empty' in str(exc.value)


def test_route_validator_invalid_response_status_code():
    route_spec = {
        "url": "/users",
        "method": HTTPMethod.GET.value,
        "response": {"status_code": "fake"},
    }

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert "'fake' is not a valid HTTPStatus" in str(exc.value)


def test_route_validator_invalid_response_sleep():
    route_spec = {
        "url": "/users",
        "method": HTTPMethod.GET.value,
        "response": {"status_code": HTTPStatus.OK.value, "sleep": "fake"},
    }

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"response.sleep" must be an int' in str(exc.value)


def test_route_validator_invalid_headers():
    route_spec = {
        "url": "/users",
        "method": HTTPMethod.GET.value,
        "response": {"status_code": HTTPStatus.OK.value, "headers": ""},
    }

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"response.headers" must be an object' in str(exc.value)
