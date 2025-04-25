from collections.abc import Iterable
from collections.abc import Iterator
from typing import Any
from typing import ClassVar
from typing import Generic
from typing import NamedTuple
from typing import TypeVar

import attrs
from domilite import tags
from markupsafe import escape
from wtforms.fields import Field
from wtforms.fields import SelectField

from bootlace.util import Tag

from .core import Widget

__all__ = ["Select", "OptionChoice"]

V = TypeVar("V")


class OptionChoice(NamedTuple, Generic[V]):
    value: V
    label: str
    selected: bool
    render_kw: dict[str, Any]

    @classmethod
    def map(cls, iterator: Iterable[tuple[V, str, bool, dict[str, Any]]]) -> "Iterator[OptionChoice]":
        for item in iterator:
            yield cls(*item)


@attrs.define
class Select(Widget):
    multiple: bool = False
    validation_attrs = {"required", "disabled"}
    tag = Tag(tags.select, classes={"form-control"})
    optgroup: ClassVar[Tag] = Tag(tags.optgroup)
    option: ClassVar[Tag] = Tag(tags.option)

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        if not isinstance(field, SelectField):
            raise TypeError(f"Field for select widget must be a SelectField, got {type(field)!r}")
        if self.multiple:
            kwargs["multiple"] = True
        widget_tag = super().__form_tag__(field, **kwargs)

        if field.has_groups():
            for group, choices in field.iter_groups():
                group_tag = self.optgroup(label=group)
                for choice in OptionChoice.map(choices):
                    group_tag.add(self.render_option(choice))
                widget_tag.add(group_tag)
        else:
            for choice in OptionChoice.map(field.iter_choices()):
                widget_tag.add(self.render_option(choice))
        return widget_tag

    def render_option(self, choice: OptionChoice) -> tags.html_tag:
        if choice.value is True:
            value = str(choice.value)
        else:
            value = choice.value
        options = dict(choice.render_kw, value=value)
        if choice.selected:
            options["selected"] = True
        return self.option(escape(choice.label), **options)
