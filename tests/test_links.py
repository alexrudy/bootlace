from flask import Flask
from flask import request

from bootlace.links import Link
from bootlace.links import View
from bootlace.testing import assert_same_html
from bootlace.util import render


def test_link() -> None:

    link = Link(text="Test", url="https://example.com")
    assert link.active is False
    assert link.enabled is True

    expected = '<a href="https://example.com">Test</a>'
    assert_same_html(expected, render(link))


def test_view(app: Flask) -> None:

    with app.test_request_context("/"):
        view = View(text="Test", endpoint="index")

        print(f"{request.endpoint=}")
        print(f"{request.url_rule=}")
        assert request.url_rule is not None
        built = request.url_rule.build({})
        print(f"{built=}")
        print(f"{request.path=}")

        assert view.active, "View should be active"
        assert view.enabled, "View should be enabled"

        expected = '<a href="/">Test</a>'
        assert_same_html(expected, render(view))

    with app.test_request_context("/"):
        view = View(text="Test", endpoint="other", ignore_query=False)
        assert not view.active, "View should not be active"

    with app.test_request_context("/foo"):
        view = View(text="Test", endpoint="index")
        assert not view.active, "View should not be active"

    with app.test_request_context("/static/foo"):
        view = View(text="Test", endpoint="static", url_kwargs={"filename": "foo.txt"})
        assert not view.active, "View should not be active"
