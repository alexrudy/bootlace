import pytest

from .conftest import CurrentLink
from .conftest import DisabledLink
from .conftest import get_fixture
from bootlace.nav import elements
from bootlace.nav import NavStyle
from bootlace.testing.html import assert_same_html
from bootlace.util import render


@pytest.fixture
def nav() -> elements.Nav:
    nav = elements.Nav()
    nav.items.append(CurrentLink.with_url(url="#", text="Active"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(DisabledLink.with_url(url="#", text="Disabled"))
    return nav


def test_base_nav(nav: elements.Nav) -> None:
    source = render(nav)

    expected = get_fixture("nav.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_nav_tabs(nav: elements.Nav) -> None:
    nav.style = NavStyle.TABS
    source = render(nav)

    expected = get_fixture("nav_tabs.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_nav_pills(nav: elements.Nav) -> None:
    nav.style = NavStyle.PILLS

    source = render(nav)

    expected = get_fixture("nav_pills.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_nav_text() -> None:
    nav = elements.Nav()
    nav.items.append(elements.Text(text="Text"))

    source = render(nav)
    expected = get_fixture("nav_text.html")
    assert_same_html(expected_html=expected, actual_html=str(source))
