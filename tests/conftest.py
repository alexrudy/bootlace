import pytest
from flask import Flask


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.config.update({"ENV": "test", "TESTING": True})

    @app.route("/")
    def index() -> str:
        return "Hello, World!"

    return app
