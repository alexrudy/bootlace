from pathlib import Path

import pytest

from bootlace.nav import bar
from bootlace.nav import elements
from bootlace.util import ids


def get_fixture(name: str) -> str:
    here = Path(__file__).parent

    if not name.endswith(".html"):
        name += ".html"

    return (here / "fixtures" / name).read_text()


class CurrentLink(elements.Link):

    @property
    def active(self) -> bool:
        return True


class DisabledLink(elements.Link):

    @property
    def enabled(self) -> bool:
        return False


@pytest.fixture
def nav() -> bar.Nav:
    ids.reset()

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
    return nav
