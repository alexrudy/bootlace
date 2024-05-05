import json

import pytest

from bootlace.nav import core
from bootlace.nav import elements


def test_nav(nav: elements.NavBar) -> None:

    data = nav.serialize()
    raw = json.dumps(data)

    print(json.dumps(data, indent=2))

    nav2 = core.NavElement.deserialize(json.loads(raw))

    assert nav == nav2


@pytest.mark.parametrize(
    "element",
    [
        elements.Link.with_url(url="#", text="Link"),
        elements.Separator(),
        elements.Text(text="Text"),
        elements.NavBar(),
        elements.Brand.with_view("home", "My Site Brand"),
        elements.NavBarCollapse(),
        elements.NavBarNav(),
        elements.NavBarSearch(),
        elements.Nav(),
        elements.Dropdown(title="Dropdown", items=[elements.Link.with_url(url="#", text="Action")]),
    ],
    ids=lambda x: x.__class__.__name__,
)
def test_scalar(element: core.NavElement) -> None:
    data = element.serialize()
    assert data["__type__"] == element.__class__.__name__

    raw = json.dumps(data)

    element2 = core.NavElement.deserialize(json.loads(raw))
    assert element == element2
