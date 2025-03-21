from unittest import mock
from unittest.mock import MagicMock

from mini_mock_server.http_server import server


@mock.patch("mini_mock_server.http_server.server.ForkingHTTPServer")
@mock.patch("mini_mock_server.http_server.server.ServerHandler")
def test_run_server(m_ServerHandler: MagicMock, m_ForkingHTTPServer: MagicMock):

    m_server = m_ForkingHTTPServer.return_value

    server.run_server("fake.json")

    assert m_server.serve_forever.call_count == 1


@mock.patch("mini_mock_server.http_server.server.ForkingHTTPServer")
@mock.patch("mini_mock_server.http_server.server.ServerHandler")
def test_interrupt_run_server(m_ServerHandler: MagicMock, m_ForkingHTTPServer: MagicMock):

    m_server = m_ForkingHTTPServer.return_value

    m_server.serve_forever.side_effect = KeyboardInterrupt("error")

    server.run_server("fake.json")

    assert m_server.serve_forever.call_count == 1
    assert m_server.server_close.call_count == 1
