import pytest
from domilite import util

from .conftest import CurrentLink
from .conftest import DisabledLink
from .conftest import get_fixture
from bootlace.image import Image
from bootlace.nav import bar
from bootlace.nav import elements
from bootlace.style import ColorClass
from bootlace.testing.html import assert_same_html
from bootlace.util import render


def test_navbar(nav: bar.NavBar) -> None:
    source = render(nav)

    expected = get_fixture("navbar.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_navbar_with_content() -> None:
    navbarnav = bar.NavBarNav(
        items=[
            CurrentLink.with_url(url="#", text="Home"),
            elements.Link.with_url(url="#", text="Link"),
            elements.Dropdown(
                title="Dropdown",
                items=[
                    elements.Link.with_url(url="#", text="Action"),
                    elements.Link.with_url(url="#", text="Another action"),
                    elements.Separator(),
                    elements.Link.with_url(url="#", text="Separated link"),
                ],
            ),
            DisabledLink.with_url(url="#", text="Disabled"),
        ]
    )

    nav = bar.NavBar(
        items=[
            bar.Brand.with_url(url="#", text="Navbar"),
            bar.NavBarCollapse(items=[navbarnav], id="navbarSupportedContent"),
            bar.NavBarSearch(),
        ],
    )

    source = render(nav)

    expected = get_fixture("navbar_content.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_brand_img() -> None:
    image = Image(
        alt="Bootstrap",
        src="/docs/5.3/assets/brand/bootstrap-logo.svg",
        width=30,
        height=24,
    )
    brand = bar.Brand.with_url(url="#", text=image)

    navbar = bar.NavBar(items=[brand], expand=None, fluid=False)

    source = render(navbar)

    expected = get_fixture("brand_img.html")

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_navbar_color() -> None:
    navbar = bar.NavBar(items=[bar.Brand.with_url(url="#", text="Navbar")], color=ColorClass.PRIMARY)

    source = render(navbar)

    expected = """
    <nav class="navbar navbar-expand-lg bg-primary">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">Navbar</a>
    </div>
    </nav>
    """

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_navbar_nocolor() -> None:
    navbar = bar.NavBar(items=[bar.Brand.with_url(url="#", text="Navbar")], color=None)

    source = render(navbar)

    expected = """
    <nav class="navbar navbar-expand-lg">
    <div class="container-fluid">
        <a class="navbar-brand" href="#">Navbar</a>
    </div>
    </nav>
    """

    assert_same_html(expected_html=expected, actual_html=str(source))


def test_dropdown_fallback() -> None:
    dropdown = (
        elements.Dropdown(
            title="Dropdown",
            items=[
                elements.Link.with_url(url="#", text="Action"),
                elements.Link.with_url(url="#", text="Another action"),
                elements.Separator(),
                elements.Link.with_url(url="#", text="Separated link"),
                util.text("Some text here"),
            ],
        ),
    )

    expected = get_fixture("dropdown.html")

    with pytest.warns(UserWarning):
        html = render(dropdown)

    print(html)

    assert_same_html(expected_html=expected, actual_html=str(html))
