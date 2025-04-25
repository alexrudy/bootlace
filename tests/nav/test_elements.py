import pytest
from domilite.dom_tag import dom_tag
from domilite.util import text
from flask import Flask

from bootlace import links
from bootlace.nav import elements
from bootlace.testing import assert_same_html
from bootlace.util import as_tag


def test_link() -> None:
    link_e = elements.Link.with_url(url="#", text="Link")

    expected = '<a class="nav-link" href="#">Link</a>'

    assert_same_html(expected, as_tag(link_e).render())
    assert link_e.url == "#"


def test_fake_bad_link() -> None:
    class BadLink(links.LinkBase):
        @property
        def active(self) -> bool:
            return False

        @property
        def enabled(self) -> bool:
            return False

        @property
        def url(self) -> str:
            return "wat"

        def __tag__(self) -> dom_tag:
            return text("wat")

    link_e = elements.Link(link=BadLink(text="Link"))
    assert as_tag(link_e).render() == "wat"


@pytest.mark.usefixtures("homepage")
def test_view(app: Flask) -> None:
    view_e = elements.Link.with_view(endpoint="index", text="View")

    with app.test_request_context("/"):
        source = as_tag(view_e).render()
    expected = '<a class="nav-link active" aria-current="page" href="/">View</a>'

    assert_same_html(expected, source)
