from typing import Any

import attrs
from dominate import tags
from flask import url_for

from bootlace.icon import Icon
from bootlace.table.base import ColumnBase
from bootlace.util import as_tag


@attrs.define
class Column(ColumnBase):

    def cell(self, value: Any) -> tags.html_tag:
        return tags.td(getattr(value, self.attribute))


@attrs.define
class EditColumn(ColumnBase):
    endpoint: str = attrs.field(default=".edit")

    def cell(self, value: Any) -> tags.html_tag:
        id = getattr(value, "id", None)
        return tags.td(tags.a(getattr(value, self.attribute), href=url_for(self.endpoint, id=id)))


@attrs.define
class CheckColumn(ColumnBase):

    yes: Icon = attrs.field(default=Icon("check", width=16, height=16))
    no: Icon = attrs.field(default=Icon("x", width=16, height=16))

    def cell(self, value: Any) -> tags.html_tag:
        if getattr(value, self.attribute):
            return tags.td(as_tag(self.yes))
        return tags.td(as_tag(self.no))


@attrs.define
class Datetime(ColumnBase):

    def cell(self, value: Any) -> tags.html_tag:
        return tags.td(getattr(value, self.attribute).isoformat())
