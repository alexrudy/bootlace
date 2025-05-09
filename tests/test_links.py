import pytest
from flask import Flask
from flask import request

from bootlace.endpoint import Endpoint
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


@pytest.mark.usefixtures("homepage")
def test_view(app: Flask) -> None:
    with app.test_request_context("/"):
        view = View(text="Test", endpoint="index")

        print(f"{request.endpoint=}")
        print(f"{request.url_rule=}")
        assert request.url_rule is not None
        built = request.url_rule.build({})
        print(f"{built=}")
        print(f"{request.path=}")

        assert view.active, f"{view} should be active"
        assert view.enabled, f"{view} should be enabled"
        assert view.blueprint is None

        expected = '<a href="/">Test</a>'
        assert_same_html(expected, render(view))

    with app.test_request_context("/"):
        view = View(text="Test", endpoint=Endpoint(name="other", ignore_query=False))
        assert not view.active, f"{view} should not be active"

    with app.test_request_context("/foo"):
        view = View(text="Test", endpoint="index")
        assert not view.active, f"{view} should not be active"

    with app.test_request_context("/static/foo"):
        view = View(
            text="Test",
            endpoint=Endpoint(name="static", url_kwargs={"filename": "foo.txt"}),
        )
        assert not view.active, f"{view} should not be active"
