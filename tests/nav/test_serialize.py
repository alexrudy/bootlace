import json

import pytest

from .conftest import get_fixture
from bootlace.nav import core
from bootlace.nav import elements
from bootlace.testing.html import assert_same_html
from bootlace.util import render


def test_nav(nav: elements.NavBar) -> None:

    schema = elements.NavBar.Schema()
    data = schema.dump(nav)

    print(json.dumps(data, indent=2))

    assert nav == schema.loads(json.dumps(data)), "Nav should round-trip"

    serialized = get_fixture("navbar.json")
    assert nav == schema.loads(serialized), "Nav should match fixture"

    source = render(schema.loads(serialized))
    expected = get_fixture("navbar.html")
    assert_same_html(expected_html=expected, actual_html=str(source))


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

    schema = element.Schema()

    data = schema.dump(element)
    assert data["__type__"] == element.__class__.__name__

    raw = json.dumps(data)

    element2 = schema.loads(raw)
    assert element == element2
