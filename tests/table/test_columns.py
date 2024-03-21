import datetime as dt

import attrs
import pytest
from flask import Flask

from bootlace.icon import Icon
from bootlace.table.base import Heading
from bootlace.table.columns import CheckColumn
from bootlace.table.columns import Datetime
from bootlace.table.columns import EditColumn
from bootlace.testing import assert_same_html
from bootlace.util import as_tag

ICON_OPEN_SVG_TAG = """<svg class="bi pe-none align-self-center me-1" role="img" width="16" height="16">"""


@attrs.define(kw_only=True)
class Item:
    editor: str = "editor"
    check: bool = True
    id: int = 1

    when: dt.datetime = dt.datetime(2021, 1, 1, 12, 18, 5)


@pytest.mark.usefixtures("homepage")
def test_edit_column(app: Flask) -> None:

    col = EditColumn(heading="Edit", attribute="editor", endpoint="index")

    th = as_tag(col.heading)

    assert str(th) == "<span>Edit</span>"

    with app.test_request_context("/"):
        td = col.cell("editor", Item())

    expected = '<td><a href="/?id=1">editor</a></td>'

    assert_same_html(expected, str(td))


def test_check_column(app: Flask) -> None:

    col = CheckColumn(heading="Check", attribute="check")

    with app.test_request_context("/"):
        td = col.cell("check", Item())

    expected = f"""
    <td>
        {ICON_OPEN_SVG_TAG}
            <use xlink:href="/static/icons/bootstrap-icons.svg#check"></use>
        </svg>
    </td>"""

    with app.test_request_context("/"):
        td = col.cell("check", Item(check=False))

    expected = f"""
    <td>
        {ICON_OPEN_SVG_TAG}
            <use xlink:href="/static/icons/bootstrap-icons.svg#x"></use>
        </svg>
    </td>"""

    assert_same_html(expected, str(td))


def test_datetime_column(app: Flask) -> None:

    col = Datetime(heading=Heading(icon=Icon("clock"), text="time"), attribute="when")

    with app.test_request_context("/"):
        th = as_tag(col.heading)

    expected_heading = f"""
    <a class="link-dark" data-bs-title="time" data-bs-toggle="tooltip" href="#">
    {ICON_OPEN_SVG_TAG}
        <use xlink:href="/static/icons/bootstrap-icons.svg#clock"></use
    </svg>
    </a>"""

    assert_same_html(expected_heading, str(th))

    td = col.cell("when", Item())

    expected = "<td>2021-01-01T12:18:05</td>"

    assert_same_html(expected, str(td))
