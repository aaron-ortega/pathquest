import json
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HOST = "0.0.0.0"
PORT = 9000


class RequestHandler(BaseHTTPRequestHandler):
    """
    Status Codes: https://www.restapitutorial.com/lessons/httpmethods.html
    """

    if sys.argv[1] == ".":
        root = str(Path.cwd())
    else:
        root = sys.argv[1]

    def do_GET(self) -> None:
        """Read files"""
        status, message = get_contents(self.root, self.path)

        self.protocol_version = "HTTP/1.1"
        self.send_response(status.value)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.wfile.write(bytes(json.dumps(message, indent=2), "utf8"))

    def do_DELETE(self) -> None:
        """Delete object or files"""
        # status, message = delete_contents(self.root, self.path)
        ...

    def do_POST(self) -> None:
        """Replace files"""
        ...

    def do_PUT(self) -> None:
        """Add files"""
        ...


def delete_contents(root: str, stem: str) -> tuple[HTTPStatus, dict]:
    """TODO: complete delete logic"""
    path = Path(root + stem).resolve()

    try:
        os.rmdir(path)
        # return HTTPStatus.OK, response
    except FileNotFoundError:
        return HTTPStatus.NOT_FOUND, f'Resource "{path}" not found!'
    except OSError:
        return HTTPStatus.BAD_REQUEST, "Can't deleted non-empty directory"

    response = json.dumps(
        {"data": {"root": root, "name": str(path), "status": "DELETED"}},
        indent=2,
    )
    return HTTPStatus.OK, response


def get_contents(root: str, stem: str) -> tuple[HTTPStatus, str]:
    """Returns contents inside a valid directory"""
    path = Path(root + stem).resolve()

    if path.is_dir():
        items = [item for item in sorted(path.iterdir())]
    elif path.is_file():
        items = [path]
    else:
        return HTTPStatus.NOT_FOUND, f'Resource "{path}" not found!'

    metadata = get_metadata(items)
    response = {"data": {"root": root, "name": str(path), "contents": metadata}}
    return HTTPStatus.OK, response


def get_metadata(items: list[Path]) -> list[dict]:
    """Returns metadata of file or directory"""
    response = []
    for item in items:
        response.append(
            {
                "name": item.name,
                "owner": item.owner(),
                # https://stackoverflow.com/questions/1861836/checking-file-permissions-in-linux-with-python
                "permission": {
                    "read": os.access(item, os.R_OK),
                    "write": os.access(item, os.W_OK),
                    "execute": os.access(item, os.X_OK),
                },
                "size": item.stat()[6],  # in bytes
                "type": "file" if item.is_file() else "directory",
            }
        )
    return response


def main() -> None:
    server = HTTPServer((HOST, PORT), RequestHandler)
    # Register the path and the entities within it
    print("Server running...")
    print(f"Listening to connections on port: {PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\nServer stopped!")


if __name__ == "__main__":
    main()
