import argparse

from mini_mock_server.http_server import server as http_server


def main():
    parser = argparse.ArgumentParser(description="Mini Mock Server")
    parser.add_argument(
        "path", type=str, default="./mock.json", help="File path (default: ./mock.json)"
    )
    parser.add_argument(
        "--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)"
    )
    parser.add_argument("--port", type=int, default="8000", help="Port number (default: 8000)")

    args = parser.parse_args()

    http_server.run_server(args.path, args.host, args.port)
