from bootlace.nav import elements, NavStyle
from bootlace.util import render
from bootlace.testing.html import assert_same_html


from .conftest import CurrentLink, DisabledLink, get_fixture


def test_base_nav() -> None:

    nav = elements.Nav()
    nav.items.append(CurrentLink.with_url(url="#", text="Active"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(DisabledLink.with_url(url="#", text="Disabled"))

    source = render(nav)

    expected = get_fixture("nav.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_nav_tabs() -> None:

    nav = elements.Nav(style=NavStyle.TABS)
    nav.items.append(CurrentLink.with_url(url="#", text="Active"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(DisabledLink.with_url(url="#", text="Disabled"))

    source = render(nav)

    expected = get_fixture("nav_tabs.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_nav_pills() -> None:

    nav = elements.Nav(style=NavStyle.PILLS)
    nav.items.append(CurrentLink.with_url(url="#", text="Active"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(elements.Link.with_url(url="#", text="Link"))
    nav.items.append(DisabledLink.with_url(url="#", text="Disabled"))

    source = render(nav)

    expected = get_fixture("nav_pills.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_nav_text() -> None:

    nav = elements.Nav()
    nav.items.append(elements.Text(text="Text"))

    source = render(nav)
    expected = get_fixture("nav_text.html")
    assert_same_html(expected_html=expected, actual_html=str(source))
