import attrs
import pytest

from bootlace.table import Column
from bootlace.table import Table
from bootlace.testing import assert_same_html


@attrs.define
class Item:
    id: int
    name: str


@pytest.fixture
def items() -> list[Item]:
    return [Item(1, "one"), Item(2, "two")]


@pytest.fixture
def table() -> type[Table]:
    class MyTable(Table):
        id: Column = Column("ID")
        name: Column = Column("Name")

    return MyTable


def test_basic_table(items: list[Item], table: type[Table]) -> None:
    assert len(table.columns) == 2

    table = table()
    rendered = table(items).render()

    print(rendered)

    expected = """
    <table class="table">
        <thead>
            <th scope="col"><span>ID</span></th>
            <th scope="col"><span>Name</span></th>
        </thead>
        <tbody>
            <tr id="item-1">
                <td>1</td>
                <td>one</td>
            </tr>
            <tr id="item-2">
                <td>2</td>
                <td>two</td>
            </tr>
        </tbody>
    </table>
    """

    assert_same_html(expected, rendered)


def test_table_with_decorated_classes(items: list[Item], table: type[Table]) -> None:
    table = table(decorated_classes=["table-striped", "table-bordered"])
    rendered = table(items).render()

    print(rendered)

    expected = """
    <table class="table table-striped table-bordered">
        <thead>
            <th scope="col"><span>ID</span></th>
            <th scope="col"><span>Name</span></th>
        </thead>
        <tbody>
            <tr id="item-1">
                <td>1</td>
                <td>one</td>
            </tr>
            <tr id="item-2">
                <td>2</td>
                <td>two</td>
            </tr>
        </tbody>
    </table>
    """

    assert_same_html(expected, rendered)
