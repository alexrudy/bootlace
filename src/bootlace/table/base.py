import inspect
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any
from typing import ClassVar

import attrs
from dominate import tags

from bootlace.icon import Icon
from bootlace.util import as_tag
from bootlace.util import maybe


@attrs.define
class Heading:
    text: str
    icon: Icon | None = attrs.field(default=None, converter=maybe(Icon))  # type: ignore

    def __tag__(self) -> tags.html_tag:
        if self.icon:
            return tags.a(
                as_tag(self.icon), href="#", data_bs_toggle="tooltip", data_bs_title=self.text, cls="link-dark"
            )
        return tags.span(self.text)


@attrs.define
class ColumnBase(ABC):
    heading: Heading = attrs.field(converter=maybe(Heading))  # type: ignore
    attribute: str | None = None

    @abstractmethod
    def cell(self, name: str, value: Any) -> tags.html_tag:
        raise NotImplementedError("Subclasses must implement this method")


def is_instance_or_subclass(val: Any, class_: type) -> bool:
    """Return True if ``val`` is either a subclass or instance of ``class_``."""
    try:
        return issubclass(val, class_)
    except TypeError:
        return isinstance(val, class_)


def _get_columns(attrs: Mapping[str, Any]) -> dict[str, ColumnBase]:
    return {
        column_name: column_value
        for column_name, column_value in attrs.items()
        if is_instance_or_subclass(column_value, ColumnBase)
    }


class TableMetaclass(type):

    columns: dict[str, ColumnBase]

    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type:
        cls = super().__new__(mcls, name, bases, namespace)
        cls.columns = mcls.get_declared_columns(cls)
        cls.columns.update(_get_columns(namespace))
        return cls

    @classmethod
    def get_declared_columns(mcls, cls: type) -> dict[str, ColumnBase]:
        mro = inspect.getmro(cls)
        # Loop over mro in reverse to maintain correct order of fields
        columns: dict[str, ColumnBase] = {}

        column_gen = (
            _get_columns(
                getattr(base, "_declared_columns", base.__dict__),
            )
            for base in mro[:0:-1]
        )

        for column_set in column_gen:
            columns.update(column_set)

        return columns


class Table(metaclass=TableMetaclass):

    decorated_classes: set[str] = set()
    columns: ClassVar[dict[str, ColumnBase]]

    def __init__(self, decorated_classes: Iterable[str] | None = None) -> None:
        if decorated_classes is None:
            self.decorated_classes = set()
        else:
            self.decorated_classes = set(decorated_classes)

    def render(self, items: list[Any]) -> tags.html_tag:
        table = tags.table(cls="table")
        table.classes.add(*self.decorated_classes)
        thead = tags.thead()
        tbody = tags.tbody()

        for _, column in self.columns.items():
            thead.add(tags.th(as_tag(column.heading), scope="col", __pretty=False))
        table.add(thead)

        for item in items:
            id = getattr(item, "id", None)
            tr = tags.tr(id=f"item-{id}" if id else None)
            for column_name, column in self.columns.items():
                td = column.cell(column_name, item)
                tr.add(td)
            tbody.add(tr)
        table.add(tbody)
        return table
