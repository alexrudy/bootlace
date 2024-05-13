from collections.abc import Iterator

import pytest
from flask import Flask


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.config.update({"ENV": "test", "TESTING": True})

    return app


@pytest.fixture
def homepage(app: Flask) -> None:
    @app.route("/")
    def index() -> str:
        return "Hello, World!"


@pytest.fixture(autouse=True, scope="function")
def ids() -> Iterator[None]:
    from bootlace.util import ids as element_id

    yield

    element_id.reset()
