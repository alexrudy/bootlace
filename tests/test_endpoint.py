import pytest
from flask import Blueprint
from flask import Flask

from bootlace.endpoint import Endpoint


@pytest.fixture
def app(app: Flask) -> Flask:

    @app.route("/")
    def home() -> str:
        return "Home"

    @app.route("/about")
    def about() -> str:
        return "About"

    @app.route("/contact")
    def contact() -> str:
        return "Contact"

    return app


@pytest.fixture
def bp(app: Flask) -> Blueprint:
    bp = Blueprint("bp", __name__)

    @bp.route("/archive")
    def archive() -> str:
        return "Archive"

    @bp.route("/post")
    def post() -> str:
        return "Post"

    app.register_blueprint(bp)

    return bp


def test_endpoint_app_url(app: Flask) -> None:

    endpoint = Endpoint(context=None, name="home")

    with app.test_request_context("/"):
        assert endpoint.url == "/"


def test_endpoint_bp_url(app: Flask, bp: Blueprint) -> None:

    endpoint = Endpoint(context=bp, name="archive")

    with app.test_request_context("/"):
        assert endpoint.url == "/archive"
