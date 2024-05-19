"""Test utils.

I've mostly just copied these from the pynetbox repository, since I didn't want
to re-invent how to mock the netbox API.

The suite still has a lackluster test coverage, but it's there, which is important.
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Type
from unittest.mock import patch

from netbox_context_edit.main import NetboxHandlerBase, NetboxObject
from netbox_context_edit.context_yaml import NetboxYamlContext
from netbox_context_edit.manager import NetboxContextManager

API_URL = "http://localhost:8000"
API_TOKEN = "test"


class Response:
    """A mock response class."""

    def __init__(self, fixture=None, status_code=200, ok=True, content=None):
        """Initialize and load fixture."""
        self.status_code = status_code
        self.content = json.dumps(content) if content else self.load_fixture(fixture)
        self.ok = ok

    def load_fixture(self, path):
        """Load fixture from path."""
        if not path:
            return "{}"
        with open(f"tests/fixtures/{path}", "r") as f:
            return f.read()

    def json(self):
        """Return fixture as JSON."""
        return json.loads(self.content)


class NBContextMock:
    """Generic netbox context mock class."""

    class Tests(unittest.TestCase):
        """Test case."""

        nb_context: str = ""
        nb_context_handler: Type[NetboxHandlerBase]
        file_handler = NetboxYamlContext

        def test_get_all(self):
            """Test that you can get all objects."""
            with patch(
                "requests.sessions.Session.get",
                return_value=Response(f"{self.nb_context}/all.json"),
            ):
                handler = self.nb_context_handler(API_URL, API_TOKEN, True)
                ret = handler.get_all()
                self.assertTrue(isinstance(ret, list))
                first_obj = next(iter(ret))
                self.assertTrue(isinstance(first_obj, NetboxObject))

        def test_get_one(self):
            """Test a single object."""
            with patch(
                "requests.sessions.Session.get",
                return_value=Response(f"{self.nb_context}/single.json"),
            ):
                handler = self.nb_context_handler(API_URL, API_TOKEN, True)
                ret = handler.get_one(name="vm-test01")
                self.assertTrue(isinstance(ret, NetboxObject))

        def test_pull(self):
            """Test pull behavior."""
            with tempfile.TemporaryDirectory() as dirname:
                directory = Path(dirname)
                with patch(
                    "requests.sessions.Session.get",
                    return_value=Response(f"{self.nb_context}/all.json"),
                ):
                    manager = NetboxContextManager(
                        API_URL,
                        API_TOKEN,
                        directory,
                        self.nb_context_handler,
                        self.file_handler,
                        test_mode=True,
                    )
                    manager.pull()
                    created_files = [
                        x
                        for x in directory.glob(f"*.{self.file_handler.file_extension}")
                    ]
                    self.assertTrue(len(created_files) == 2)
