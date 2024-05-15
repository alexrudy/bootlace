import datetime as dt

import attrs
import pytest
from flask import Flask

from bootlace.extension import Bootlace
from bootlace.icon import Icon
from bootlace.table.base import Heading
from bootlace.table.columns import CheckColumn
from bootlace.table.columns import Column
from bootlace.table.columns import Datetime
from bootlace.table.columns import EditColumn
from bootlace.testing import assert_same_html
from bootlace.util import as_tag

ICON_OPEN_SVG_TAG = """<svg class="bi pe-none align-self-center me-1" role="img" width="16" height="16">"""


@pytest.fixture
def app(app: Flask) -> Flask:
    Bootlace(app)
    return app


@attrs.define(kw_only=True)
class Item:
    editor: str = "editor"
    check: bool = True
    id: int = 1
    missing: str | None = None

    when: dt.datetime = dt.datetime(2021, 1, 1, 12, 18, 5)


def test_unnamed_column() -> None:

    col = EditColumn(heading="Edit", endpoint="index")

    with pytest.raises(ValueError):
        col.attribute


@pytest.mark.usefixtures("homepage")
def test_edit_column(app: Flask) -> None:

    col = EditColumn(heading="Edit", name="editor", endpoint="index")

    th = as_tag(col.heading)

    assert str(th) == "<span>Edit</span>"

    with app.test_request_context("/"):
        td = col.cell(Item())

    expected = '<td><a href="/?id=1">editor</a></td>'

    assert_same_html(expected, str(td))


def test_check_column(app: Flask) -> None:

    col = CheckColumn(heading="Check", name="check")

    with app.test_request_context("/"):
        td = col.cell(Item())

    expected = f"""
    <td>
        {ICON_OPEN_SVG_TAG}
            <use xlink:href="/static/icons/bootstrap-icons.svg#check"></use>
        </svg>
    </td>"""

    with app.test_request_context("/"):
        td = col.cell(Item(check=False))

    expected = f"""
    <td>
        {ICON_OPEN_SVG_TAG}
            <use xlink:href="/static/icons/bootstrap-icons.svg#x"></use>
        </svg>
    </td>"""

    assert_same_html(expected, str(td))


def test_datetime_column(app: Flask) -> None:

    col = Datetime(heading=Heading(icon=Icon("clock"), text="time"), name="when")

    with app.test_request_context("/"):
        th = as_tag(col.heading)

    expected_heading = f"""
    <a class="link-dark" data-bs-title="time" data-bs-toggle="tooltip" href="#">
    {ICON_OPEN_SVG_TAG}
        <use xlink:href="/static/icons/bootstrap-icons.svg#clock"></use
    </svg>
    </a>"""

    assert_same_html(expected_heading, str(th))

    td = col.cell(Item())

    expected = "<td>2021-01-01T12:18:05</td>"

    assert_same_html(expected, str(td))


def test_datetime_format() -> None:

    col = Datetime(heading="Date", name="when", format="%Y-%m-%d")

    td = col.cell(Item())

    expected = "<td>2021-01-01</td>"

    assert_same_html(expected, str(td))


def test_regular_column_missing() -> None:

    col = Column(heading="Something", name="missing")

    td = col.cell(Item())
    expected = "<!--no value for missing-->"
    assert str(td) == expected
