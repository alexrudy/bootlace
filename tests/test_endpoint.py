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


def test_endpoint_bp_url_no_context(app: Flask, bp: Blueprint) -> None:
    endpoint = Endpoint(context=None, name=f"{bp.name}.archive")

    with app.test_request_context("/"):
        assert endpoint.url == "/archive"


def test_endpoint_attributes(app: Flask, bp: Blueprint) -> None:
    endpoint = Endpoint(context=bp, name="archive")

    with app.test_request_context("/archive"):
        assert endpoint.full_name == "bp.archive"
        assert endpoint.blueprint == "bp"
        assert endpoint.url == "/archive"
        assert endpoint.active is True
        assert endpoint() == "/archive"
        assert endpoint(query="a") == "/archive?query=a"

    with app.test_request_context("/"):
        assert endpoint.active is False

    with app.test_request_context("/archive?query=a"):
        assert endpoint.active is True

    endpoint = Endpoint(context=None, name="home")
    assert endpoint.blueprint is None


def test_endpoint_active_context_with_fullname(app: Flask, bp: Blueprint) -> None:
    endpoint = Endpoint(context=bp, name="bp.archive")

    with app.test_request_context("/archive"):
        assert endpoint.active is True
        assert endpoint.blueprint == "bp"
