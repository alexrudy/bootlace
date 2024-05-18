import inspect
from abc import ABC
from abc import abstractmethod
from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any
from typing import ClassVar

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag
from dominate.util import text

from bootlace.icon import Icon
from bootlace.util import as_tag
from bootlace.util import maybe
from bootlace.util import Tag


@attrs.define
class Heading:
    """A heading for a table column."""

    #: The text of the heading
    text: str

    #: The icon for the heading, in place of the text
    icon: Icon | None = attrs.field(default=None, converter=maybe(Icon))  # type: ignore

    def __tag__(self) -> tags.html_tag:
        if self.icon:
            return tags.a(
                as_tag(self.icon), href="#", data_bs_toggle="tooltip", data_bs_title=self.text, cls="link-dark"
            )
        return tags.span(self.text)


@attrs.define
class ColumnBase(ABC):
    """Base class for table columns.

    Subclasses must implement the :meth:`cell` method."""

    #: The heading for the column
    heading: Heading = attrs.field(converter=maybe(Heading))  # type: ignore

    name: str | None = None

    th = Tag(tags.th)
    td = Tag(tags.td)

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = self.name or name

    @property
    def attribute(self) -> str:
        """The attribute name for the column."""
        if self.name is None:
            raise ValueError("column must be named in Table or name= parameter must be provided")
        return self.name

    def contents(self, value: Any, format: str | None = None) -> Any:
        """Return the contents of the cell for the column, using an HTML comment if the attribute value is None."""
        contents = getattr(value, self.attribute)
        if contents is None:
            return tags.comment(f"No value for {self.name}")
        if format:
            return text(format.format(contents))
        return text(str(contents))

    @abstractmethod
    def cell(self, value: Any) -> dom_tag:
        """Return the cell for the column as an HTML tag."""
        raise NotImplementedError("Subclasses must implement this method")

    def __th__(self) -> dom_tag:
        return self.th(as_tag(self.heading), scope="col", __pretty=False)

    def __td__(self, value: Any) -> dom_tag:
        return self.td(self.cell(value), __pretty=False)


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
    """Base class for class-defined tables.

    Subclasses should define columns as class attributes, e.g.:

    class MyTable(Table):
        name = Column(Heading("Name"))
        age = Column(Heading("Age"))

    Use :meth:`render` to render a table from a list of items as
    :class:`dominate.tags.table`.
    """

    columns: ClassVar[dict[str, ColumnBase]]

    table = Tag(tags.table)
    thead = Tag(tags.thead)
    tbody = Tag(tags.tbody)
    tr = Tag(tags.tr)

    def __init__(self, decorated_classes: Iterable[str] | None = None) -> None:
        if decorated_classes is None:
            self.decorated_classes = set()
        else:
            self.decorated_classes = set(decorated_classes)

    def __table__(self, items: list[Any]) -> tags.html_tag:
        table = self.table(cls="table")
        table.classes.add(*self.decorated_classes)
        table.add(self.__thead__())
        table.add(self.__tbody__(items))
        return table

    def __thead__(self) -> tags.html_tag:
        thead = self.thead()
        for column in self.columns.values():
            thead.add(column.__th__())
        return thead

    def __tr__(self, item: Any) -> tags.html_tag:
        id = getattr(item, "id", None)
        name = item.__class__.__name__.lower()
        tr = self.tr(id=f"{name}-{id}" if id else None)
        for column in self.columns.values():
            tr.add(column.__td__(item))
        return tr

    def __tbody__(self, items: list[Any]) -> tags.html_tag:
        tbody = self.tbody()
        for item in items:
            tbody.add(self.__tr__(item))
        return tbody

    def __call__(self, items: list[Any]) -> tags.html_tag:
        return self.__table__(items)
