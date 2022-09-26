import unittest
from http import HTTPStatus
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch

from app import RequestHandler, get_contents, get_metadata


class TestDoGet(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_request = Mock()

    @patch("http.server.HTTPServer")
    @patch("app.RequestHandler.do_GET")
    def test_do_get(self, mock_do_get, mock_http_server):
        """Test if do_GET method gets called"""
        mock_do_get.return_value = "/"
        self.mock_request.makefile.return_value = BytesIO(b"GET /")
        server = RequestHandler(
            self.mock_request, ("127.0.0.1", 8080), mock_http_server
        )
        self.assertTrue(mock_do_get.called)
        self.assertEqual(server.do_GET(), "/")


class TestGetMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.path = Path("__file__").parent.resolve()
        # Create temp file and directory
        self.tmp_file = self.path.joinpath("foo.txt")
        self.tmp_dir = self.path.joinpath("bar")
        self.tmp_file.touch()
        self.tmp_dir.mkdir()
        self.maxDiff = None

    def tearDown(self) -> None:
        self.tmp_file.unlink()
        self.tmp_dir.rmdir()

    def test_get_metadata(self) -> None:
        single_file_response = get_metadata([self.tmp_file])
        single_dir_response = get_metadata([self.tmp_dir])
        dir_and_file_response = get_metadata([self.tmp_dir, self.tmp_file])

        expected_file_output = {
            "name": "foo.txt",
            "owner": "aaronortega",
            "permission": {"read": True, "write": True, "execute": False},
            "size": 0,
            "type": "file",
        }
        expected_dir_ouput = {
            "name": "bar",
            "owner": "aaronortega",
            "permission": {"execute": True, "read": True, "write": True},
            "size": 64,
            "type": "directory",
        }
        expected_result = [expected_dir_ouput, expected_file_output]

        self.assertListEqual(single_file_response, [expected_file_output])
        self.assertListEqual(single_dir_response, [expected_dir_ouput])
        self.assertListEqual(dir_and_file_response, expected_result)

    def test_get_contents(self) -> None:
        invalid_file_response = get_contents("foo", "bar")
        self.assertEquals(
            HTTPStatus.NOT_FOUND.value, invalid_file_response["status"]["code"]
        )
        self.assertDictEqual(
            invalid_file_response,
            {
                "status": {
                    "code": 404,
                    "description": "Nothing matches the given URI",
                    "message": "Resource "
                    "'/Users/aaronortega/open-source-projects/pathquest/foobar' "
                    "not found!",
                }
            },
        )

        response = get_contents(str(self.path) + "/", self.tmp_file.name)
        self.assertEquals(HTTPStatus.OK.value, response["status"]["code"])
        self.assertDictEqual(
            response,
            {
                "data": {
                    "contents": [
                        {
                            "name": "foo.txt",
                            "owner": "aaronortega",
                            "permission": {
                                "execute": False,
                                "read": True,
                                "write": True,
                            },
                            "size": 0,
                            "type": "file",
                        }
                    ],
                    "name": "/Users/aaronortega/open-source-projects/pathquest/foo.txt",
                    "root": "/Users/aaronortega/open-source-projects/pathquest/",
                },
                "status": {
                    "code": 200,
                    "message": "Request fulfilled, document follows",
                },
            },
        )


class TestMetaData(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
