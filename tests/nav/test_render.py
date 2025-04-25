import pytest
from flask import Flask

from bootlace.links import View
from bootlace.nav import NavAlignment
from bootlace.nav import NavStyle
from bootlace.nav import core
from bootlace.nav import elements
from bootlace.testing.html import assert_same_html
from bootlace.util import render

from .conftest import CurrentLink


def test_plain_element() -> None:
    nav = elements.Nav()
    nav.items.append(core.NavElement())

    with pytest.warns(UserWarning):
        source = render(nav)

    expected = "<ul class='nav'><li class='nav-item'><!-- Warning about unhandled element --></li></ul>"

    assert_same_html(expected_html=expected, actual_html=str(source))


@pytest.mark.parametrize(
    "alignment, cls",
    [
        (NavAlignment.DEFAULT, None),
        (NavAlignment.FILL, "nav-fill"),
        (NavAlignment.JUSTIFIED, "nav-justified"),
    ],
    ids=["default", "fill", "justified"],
)
def test_nav_alignment(alignment: core.NavAlignment, cls: str) -> None:
    nav = elements.Nav(alignment=alignment)
    nav.items.append(elements.Text("Text"))

    source = render(nav)
    expected = f"""
    <ul class='nav {cls if cls else ""}'>
        <li class='nav-item'><span class='nav-link disabled' aria-disabled='true'>Text</span></li>
    </ul>"""

    assert_same_html(expected_html=expected, actual_html=str(source))


@pytest.mark.parametrize(
    "style",
    [
        NavStyle.PLAIN,
        NavStyle.TABS,
        NavStyle.PILLS,
    ],
    ids=["default", "tabs", "pills"],
)
def test_nav_style(style: NavStyle) -> None:
    nav = elements.Nav(style=style)
    nav.items.append(elements.Text("Text"))

    source = render(nav)
    expected = f"""
    <ul class='nav {style.value}'>
        <li class='nav-item'><span class='nav-link disabled' aria-disabled='true'>Text</span></li>
    </ul>"""
    assert not nav.active, "No item should be active"

    assert_same_html(expected_html=expected, actual_html=str(source))


@pytest.mark.usefixtures("homepage")
def test_nav_active_endpoint(app: Flask) -> None:
    nav = elements.Nav()
    nav.items.append(CurrentLink(link=View(text="Active", endpoint="index")))

    with app.test_request_context("/"):
        source = render(nav)
        assert nav.active, "The first item should be active"
    expected = "<ul class='nav'><li class='nav-item'><a class='nav-link active' aria-current='page' href='/'>Active</a></li></ul>"

    assert_same_html(expected_html=expected, actual_html=str(source))
