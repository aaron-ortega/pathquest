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

    def write_header(self, code) -> None:
        self.protocol_version = "HTTP/1.1"
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def write_response(self, response) -> None:
        self.wfile.write(bytes(json.dumps(response, indent=2), "utf8"))

    def action_not_implemented(self) -> None:
        response = {
            "status": {
                "code": HTTPStatus.NOT_IMPLEMENTED.value,
                "description": HTTPStatus.NOT_IMPLEMENTED.description,
            }
        }
        self.write_header(response["status"]["code"])
        self.write_response(response)

    def do_GET(self) -> None:
        """Read files"""
        response = get_contents(self.root, self.path)

        self.write_header(response["status"]["code"])
        self.write_response(response)

    def do_DELETE(self) -> None:
        """Delete object or files"""
        # status, message = delete_contents(self.root, self.path)
        self.action_not_implemented()

    def do_POST(self) -> None:
        """Replace files"""
        self.action_not_implemented()

    def do_PUT(self) -> None:
        """Add files"""
        self.action_not_implemented()


def delete_contents(root: str, stem: str) -> tuple[HTTPStatus, dict]:
    """
    TODO: In progress
    Following cases need handling:
        - If object is valid and exists, then delete and return 200
        - If object doesn't exist, then do nothing and return 204
        - If object is non-empty directory, then do nothing and return 400; no recursive deletion
    """
    path = Path(root + stem).resolve()

    try:
        os.rmdir(path)
    except FileNotFoundError:
        return {
            "code": HTTPStatus.NOT_FOUND.value,
            "description": HTTPStatus.NOT_FOUND.description,
            "message": f'Resource "{path}" not found!',
        }
    except OSError:
        return {
            "code": HTTPStatus.BAD_REQUEST.value,
            "description": HTTPStatus.BAD_REQUEST.description,
            "message": "Can't deleted non-empty directory",
        }

    return {
        "data": {
            "root": root,
            "name": str(path),
            "status": {
                "code": HTTPStatus.OK.value,
                "description": HTTPStatus.OK.description,
                "message": f"Resource '{path}' deleted!",
            },
        }
    }


def get_contents(root: str, stem: str) -> tuple[HTTPStatus, str]:
    """Returns contents inside a valid directory"""
    path = Path(root + stem).resolve()

    if path.is_dir():
        items = [item for item in sorted(path.iterdir())]
    elif path.is_file():
        items = [path]
    else:
        return {
            "status": {
                "code": HTTPStatus.NOT_FOUND.value,
                "description": HTTPStatus.NOT_FOUND.description,
                "message": f"Resource '{path}' not found!",
            }
        }

    metadata = get_metadata(items)
    response = {
        "data": {"root": root, "name": str(path), "contents": metadata},
        "status": {"code": HTTPStatus.OK.value, "message": HTTPStatus.OK.description},
    }
    return response


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
