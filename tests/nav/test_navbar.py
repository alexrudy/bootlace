from bootlace.nav import elements
from bootlace.nav import bar
from bootlace.image import Image
from bootlace.util import render
from bootlace.testing.html import assert_same_html

from .conftest import CurrentLink, DisabledLink, get_fixture


def test_navbar() -> None:
    nav = bar.NavBar(
        items=[
            bar.Brand.with_url(url="#", text="Navbar"),
            bar.NavBarCollapse(
                id="navbarSupportedContent",
                items=[
                    bar.NavBarNav(
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
                    ),
                    bar.NavBarSearch(),
                ],
            ),
        ],
    )

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

    image = Image(alt="Bootstrap", src="/docs/5.3/assets/brand/bootstrap-logo.svg", width=30, height=24)
    brand = bar.Brand.with_url(url="#", text=image)

    navbar = bar.NavBar(items=[brand], expand=None, fluid=False)

    source = render(navbar)

    expected = get_fixture("brand_img.html")

    assert_same_html(expected_html=expected, actual_html=str(source))
