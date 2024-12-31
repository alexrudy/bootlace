from typing import Any

import pytest
from dominate import tags
from flask import Blueprint
from flask import Flask
from flask import request

from bootlace.util import as_tag
from bootlace.util import is_active_blueprint
from bootlace.util import is_active_endpoint
from bootlace.util import Tag


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

    @bp.route("/post/<id>")
    def post(id: str) -> str:
        return "Post"

    app.register_blueprint(bp)

    return bp


class Taggable:
    def __tag__(self) -> tags.html_tag:
        return tags.div()


@pytest.mark.parametrize(
    "tag,expected",
    [
        (tags.div(), "<div></div>"),
        (Taggable(), "<div></div>"),
        ("test", "test"),
        (["test", "test2"], "testtest2"),
        (["test", tags.div()], "test\n<div></div>\n"),
    ],
    ids=["tag", "taggable", "str", "list", "list-tag"],
)
def test_as_tag(tag: Any, expected: str) -> None:
    assert as_tag(tag).render() == expected


def test_as_tag_warning() -> None:
    with pytest.warns(UserWarning):
        assert as_tag(1).render() == "1\n<!--Rendered type int not supported-->\n"


def test_classes() -> None:

    div = tags.div()

    div.classes.add("test")
    div.classes.add("test")

    assert "test" in div.classes

    assert div.render() == '<div class="test"></div>'

    div.classes.swap("test", "other")
    div.classes.swap("test", "other")

    assert div.render() == '<div class="other"></div>'

    assert len(div.classes) == 1

    div.classes.remove("other")

    assert div.render() == '<div class=""></div>'

    div.classes.add("test")
    div.classes.add("other")
    div.classes.discard("test")
    assert div.render() == '<div class="other"></div>'


@pytest.mark.parametrize("prefix", ["data", "aria", "hx"])
def test_accessors(prefix: str) -> None:
    div = tags.div(other="ignored")

    pa = getattr(div, prefix)
    assert pa is not None

    pa["test"] = "test"
    assert div[f"{prefix}-test"] == "test"
    assert pa["test"] == "test"

    del pa["test"]
    assert f"{prefix}-test" not in div.attributes

    tag = pa.set("other-test", "other-value")
    assert tag == div
    assert tag[f"{prefix}-other-test"] == "other-value"

    tag = pa.remove("other-test")
    assert tag == div
    assert f"{prefix}-other-test" not in div.attributes

    div[f"{prefix}-parent-test"] = "test-4"
    assert pa["parent-test"] == "test-4"
    del div[f"{prefix}-parent-test"]

    pa["test1"] = "value-1"
    pa["test2"] = "value-2"
    assert len(pa) == 2
    assert set(pa) == {"test1", "test2"}


def test_tag_configurator() -> None:

    a = Tag(tags.a, classes={"test"}, attributes={"href": "#"})

    assert a["href"] == "#"
    a["href"] = "/test"
    a.classes.add("other")
    a.classes.discard("test")

    assert as_tag(a).render() == '<a class="other" href="/test"></a>'


@pytest.mark.usefixtures("bp")
@pytest.mark.parametrize(
    "uri,endpoint,kwargs,expected",
    [
        ("/", "home", {}, True),
        ("/about", "home", {}, False),
        ("/post/a", "bp.post", {"id": "a"}, True),
        ("/post/b", "bp.post", {"id": "a"}, False),
        ("/archive", "bp.archive", {}, True),
    ],
)
def test_is_active_endpoint(app: Flask, uri: str, endpoint: str, kwargs: dict[str, str], expected: bool) -> None:

    with app.test_request_context(uri):
        print(f"Testing {uri} -> {endpoint} with {kwargs}")
        assert is_active_endpoint(endpoint, kwargs) is expected


@pytest.mark.usefixtures("bp")
def test_is_active_endpoint_invalid_kwargs(app: Flask) -> None:

    with app.test_request_context("/"):
        assert request.endpoint == "home"
        assert request.url_rule is not None
        assert not is_active_endpoint("home", {"id": "a"}, ignore_query=False)


@pytest.mark.usefixtures("bp")
@pytest.mark.parametrize(
    "uri,blueprint,expected",
    [
        ("/", None, True),
        ("/about", "bp", False),
        ("/post/a", "bp", True),
        ("/archive", "bp", True),
    ],
)
def test_is_active_blueprint(app: Flask, uri: str, blueprint: str, expected: bool) -> None:

    with app.test_request_context(uri):
        print(f"Testing {uri} -> {blueprint}")
        assert is_active_blueprint(blueprint) is expected
