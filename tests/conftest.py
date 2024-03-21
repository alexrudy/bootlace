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
