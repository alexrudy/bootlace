from flask import Flask

from bootlace.nav import elements
from bootlace.testing import assert_same_html
from bootlace.util import as_tag


def test_link() -> None:
    link_e = elements.Link.with_url(url="#", text="Link")

    expected = '<a class="nav-link" href="#">Link</a>'

    assert_same_html(expected, as_tag(link_e).render())
    assert link_e.url == "#"


def test_view(app: Flask) -> None:
    view_e = elements.Link.with_view(endpoint="index", text="View")

    with app.test_request_context("/"):
        source = as_tag(view_e).render()
    expected = '<a class="nav-link" href="/">View</a>'

    assert_same_html(expected, source)
