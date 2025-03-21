import pytest

from mini_mock_server.validators.route import validator as route_validator


def test_route_validator_no_url():
    route_spec = {}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"url" key is required' in str(exc.value)


def test_route_validator_no_method():
    route_spec = {"url": "/users"}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert '"method" key is required' in str(exc.value)


def test_route_validator_invalid_method():
    route_spec = {"url": "/users", "method": "fake"}

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert "'FAKE' is not a valid HTTPMethod" in str(exc.value)


def test_route_validator_invalid_routes():
    route_spec = ""

    with pytest.raises(ValueError) as exc:
        route_validator.validate("/", route_spec, 1)

    assert "Route must be an object" in str(exc.value)
