from unittest import mock
from unittest.mock import MagicMock
from http import HTTPMethod, HTTPStatus

from mini_mock_server.http_server.request import Request
from mini_mock_server.http_server.response import Response


def test_handle_success():
    url = "/fake"

    routes = [
        {
            "url": url,
            "method": HTTPMethod.GET.value,
            "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
        },
    ]

    m_server = MagicMock(path=url)

    request = Request(m_server, routes)

    request.handle(HTTPMethod.GET)

    expected = Response.to_json({"fake": "fake"})

    m_server.wfile.write.assert_called_once_with(expected)


def test_handle_success_list_response():
    url = "/fake"

    routes = [
        {
            "url": url,
            "method": HTTPMethod.GET.value,
            "response": [{"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}}],
        },
    ]

    m_server = MagicMock(path=url)

    request = Request(m_server, routes)

    request.handle(HTTPMethod.GET)

    expected = Response.to_json({"fake": "fake"})

    m_server.wfile.write.assert_called_once_with(expected)


@mock.patch("mini_mock_server.http_server.request.time")
def test_handle_success_sleep(m_time: MagicMock):
    url = "/fake"

    routes = [
        {
            "url": url,
            "method": HTTPMethod.GET.value,
            "response": {
                "sleep": 3,
                "status_code": HTTPStatus.OK.value,
                "body": {"fake": "fake"},
            },
        },
    ]

    m_server = MagicMock(path=url)

    request = Request(m_server, routes)

    request.handle(HTTPMethod.GET)

    expected = Response.to_json({"fake": "fake"})

    m_server.wfile.write.assert_called_once_with(expected)

    assert m_time.sleep.call_count == 1


def test_handle_not_found():
    routes = [
        {
            "url": "/fake",
            "method": HTTPMethod.GET.value,
            "response": {"status_code": HTTPStatus.OK.value, "body": {"fake": "fake"}},
        },
    ]

    m_server = MagicMock(path="/not-found")

    request = Request(m_server, routes)

    request.handle(HTTPMethod.GET)

    expected = Response.to_json({"error": HTTPStatus.NOT_FOUND.phrase})

    m_server.wfile.write.assert_called_once_with(expected)
