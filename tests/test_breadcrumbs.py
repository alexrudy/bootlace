import pytest
from flask import Blueprint
from flask import Flask

from bootlace.breadcrumbs import BreadcrumbExtension
from bootlace.breadcrumbs import breadcrumbs
from bootlace.breadcrumbs import Endpoint
from bootlace.breadcrumbs import KeywordArguments
from bootlace.testing import assert_same_html
from bootlace.util import as_tag


@pytest.fixture
def app(app: Flask) -> Flask:
    breadcrumbs = BreadcrumbExtension(app)

    @app.route("/")
    @breadcrumbs.register(None, None, "Home")
    def home() -> str:
        return "Home"

    @app.route("/about")
    @breadcrumbs.register(None, "home", "About")
    def about() -> str:
        return "About"

    @app.route("/contact")
    @breadcrumbs.register(None, "home", "Contact")
    def contact() -> str:
        return "Contact"

    return app


@pytest.fixture
def breadcrumb_extension(app: Flask) -> BreadcrumbExtension:
    return app.extensions["bootlace.breadcrumbs"]


@pytest.fixture
def bp(app: Flask, breadcrumb_extension: BreadcrumbExtension) -> Blueprint:
    bp = Blueprint("bp", __name__)

    @bp.route("/archive")
    @breadcrumb_extension.register(bp, "home", "Archive")
    def archive() -> str:
        return "Archive"

    @bp.route("/post")
    @breadcrumb_extension.register(bp, ".archive", "Post")
    def post() -> str:
        return "Post"

    app.register_blueprint(bp)

    return bp


def test_breadcrumbs_init() -> None:
    breadcrumbs = BreadcrumbExtension()
    assert breadcrumbs.tree == {}


def test_basic_breadcrumbs(app: Flask) -> None:

    with app.test_request_context("/"):
        trail = breadcrumbs.get()
        assert len(trail) == 1
        assert trail[0].title == "Home"

    with app.test_request_context("/about"):
        trail = breadcrumbs.get()
        assert len(trail) == 2
        assert trail[0].title == "Home"
        assert trail[1].title == "About"


@pytest.mark.usefixtures("bp")
def test_blueprint_breadcrumbs(app: Flask) -> None:

    with app.test_request_context("/post"):
        trail = breadcrumbs.get()
        assert len(trail) == 3
        assert trail[0].title == "Home"
        assert trail[1].title == "Archive"
        assert trail[2].title == "Post"


def test_render_single_breadcrumb(app: Flask) -> None:
    with app.test_request_context("/"):
        trail = breadcrumbs.get()
        html = as_tag(trail).render()

        expected = """
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item active" aria-current="page">Home</li>
            </ol>
        </nav>
        """

        assert_same_html(expected, html)


def test_render_nested_breadcrumbs(app: Flask) -> None:
    with app.test_request_context("/about"):
        trail = breadcrumbs.get()
        html = as_tag(trail).render()

        expected = """
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item"><a href="/">Home</a></li>
                <li class="breadcrumb-item active" aria-current="page">About</li>
            </ol>
        </nav>
        """

        assert_same_html(expected, html)


def test_render_empty_breadcrumbs(app: Flask) -> None:

    @app.route("/empty")
    def empty() -> str:
        return "Empty"

    with app.test_request_context("/empty"):
        trail = breadcrumbs.get()
        html = as_tag(trail).render()
        assert html == ""


def test_render_default_divider(app: Flask) -> None:

    app.config["BOOTLACE_BREADCRUMBS_DIVIDER"] = "/"

    with app.test_request_context("/"):
        trail = breadcrumbs.get()
        html = as_tag(trail).render()

        assert trail.divider == "/"

        expected = """
        <nav aria-label="breadcrumb">
            <ol class="breadcrumb">
                <li class="breadcrumb-item active" aria-current="page">Home</li>
            </ol>
        </nav>
        """

        assert_same_html(expected, html)


def test_register_with_app(app: Flask, breadcrumb_extension: BreadcrumbExtension) -> None:

    @app.route("/register")
    @breadcrumb_extension.register(app, None, "Register")
    def register() -> str:
        return "Register"

    with app.test_request_context("/register"):
        trail = breadcrumbs.get()
        assert len(trail) == 1
        assert trail[0].title == "Register"


def test_register_relative(app: Flask, breadcrumb_extension: BreadcrumbExtension) -> None:

    with pytest.raises(ValueError):

        @app.route("/register")
        @breadcrumb_extension.register(app, ".home", "Register")
        def register() -> str:
            return "Register"


def test_register_self_parent(app: Flask, breadcrumb_extension: BreadcrumbExtension) -> None:

    with pytest.raises(ValueError):

        @app.route("/register")
        @breadcrumb_extension.register(app, "register", "Register")
        def register() -> str:
            return "Register"


def test_kwargs_frozen() -> None:

    kwargs = KeywordArguments()
    assert len(kwargs) == 0

    with pytest.raises(TypeError):
        kwargs["foo"] = "bar"  # type: ignore

    assert list(kwargs) == []
    assert kwargs.as_dict() == {}

    kwargs = KeywordArguments(foo="bar")

    assert len(kwargs) == 1
    assert kwargs["foo"] == "bar"


def test_endpoint_invalid_name(app: Flask) -> None:

    with pytest.raises(ValueError):
        Endpoint(None, "too.many.dots")


def test_endpoint_app_url(app: Flask) -> None:

    endpoint = Endpoint(None, "home")

    with app.test_request_context("/"):
        assert endpoint.url == "/"


def test_endpoint_bp_url(app: Flask, bp: Blueprint) -> None:

    endpoint = Endpoint(bp, "archive")

    with app.test_request_context("/"):
        assert endpoint.url == "/archive"
