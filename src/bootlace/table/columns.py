from typing import Any

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag
from dominate.util import text
from flask import url_for

from bootlace.icon import Icon
from bootlace.table.base import ColumnBase
from bootlace.util import as_tag


__all__ = ["Column", "EditColumn", "CheckColumn", "Datetime"]


@attrs.define
class Column(ColumnBase):
    """A column in a table, which shows the value of an attribute.

    No special formatting is applied to the attribute, it is rendered as text."""

    def cell(self, value: Any) -> dom_tag:
        """Return the cell for the column as an HTML tag."""
        return text(str(getattr(value, self.attribute)))


@attrs.define
class EditColumn(ColumnBase):
    """A column which links to an edit view for the value.

    This is commonly shown as e.g. the name of the item, which links to the edit view."""

    #: The endpoint for the edit view
    endpoint: str = attrs.field(default=".edit")

    def cell(self, value: Any) -> tags.html_tag:
        """Return the cell for the column as an HTML tag."""
        id = getattr(value, "id", None)
        return tags.a(getattr(value, self.attribute), href=url_for(self.endpoint, id=id))


@attrs.define
class CheckColumn(ColumnBase):
    """A column which shows a checkmark or X based on the value of the attribute."""

    #: The icon for a true value
    yes: Icon = attrs.field(default=Icon("check", width=16, height=16))

    #: The icon for a false value
    no: Icon = attrs.field(default=Icon("x", width=16, height=16))

    def cell(self, value: Any) -> dom_tag:
        """Return the cell for the column as an HTML tag."""
        if getattr(value, self.attribute):
            return as_tag(self.yes)
        return as_tag(self.no)


@attrs.define
class Datetime(ColumnBase):
    """A column which shows a datetime attribute as an ISO formatted string."""

    def cell(self, value: Any) -> dom_tag:
        """Return the cell for the column as an HTML tag."""
        return text(getattr(value, self.attribute).isoformat())
