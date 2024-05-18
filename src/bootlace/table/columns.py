from typing import Any

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag
from dominate.util import text

from bootlace.endpoint import convert_endpoint
from bootlace.endpoint import Endpoint
from bootlace.icon import Icon
from bootlace.table.base import ColumnBase
from bootlace.util import as_tag
from bootlace.util import MaybeTaggable
from bootlace.util import Tag

__all__ = ["Column", "ActionColumn", "CheckColumn", "Datetime"]


@attrs.define
class Column(ColumnBase):
    """A column in a table, which shows the value of an attribute.

    If no special formatting is applied to the attribute, it is rendered as text.
    """

    format: str | None = attrs.field(default=None)

    def cell(self, value: Any) -> dom_tag:
        """Return the cell for the column as an HTML tag."""
        return self.contents(value)

    def contents(self, value: Any, format: str | None = None) -> dom_tag:
        """Return the contents of the cell for the column, using an HTML comment if the attribute value is None."""
        return super().contents(value, format or self.format)


@attrs.define
class CheckColumn(ColumnBase):
    """A column which shows a checkmark or X based on the value of the attribute."""

    #: The icon for a true value
    yes: Icon = attrs.field(default=Icon("check"))

    #: The icon for a false value
    no: Icon = attrs.field(default=Icon("x"))

    def cell(self, value: Any) -> dom_tag:
        """Return the cell for the column as an HTML tag."""
        if getattr(value, self.attribute):
            return as_tag(self.yes)
        return as_tag(self.no)


@attrs.define
class Datetime(ColumnBase):
    """A column which shows a datetime attribute as an ISO formatted string.

    This column can also be used for date or time objects.

    A format string can be provided to format the datetime object."""

    format: str | None = attrs.field(default=None)

    def cell(self, value: Any) -> dom_tag:
        """Return the cell for the column as an HTML tag."""
        if self.format:
            return text(getattr(value, self.attribute).strftime(self.format))

        return text(getattr(value, self.attribute).isoformat())


@attrs.define
class ActionColumn(ColumnBase):
    """
    A column which links to a view for the value.

    This is commonly shown as e.g. the name of the item, which links to the edit view.
    """

    endpoint: Endpoint = attrs.field(default=Endpoint.from_name(".edit"), converter=convert_endpoint)

    label: MaybeTaggable = attrs.field(default=None)

    a: Tag = Tag(tags.a)

    def cell(self, value: Any) -> tags.html_tag:
        id = getattr(value, "id", None)

        if self.label is None:
            contents = self.contents(value)
        else:
            contents = as_tag(self.label)

        return self.a(contents, href=self.endpoint(id=id))
