from typing import Any

import attrs
from domilite.tags import html_tag
from domilite.tags import input
from wtforms.fields.core import Field

from bootlace.util import Tag

from .core import InputBase

__all__ = [
    "SearchInput",
    "TelInput",
    "URLInput",
    "EmailInput",
    "DateTimeInput",
    "DateInput",
    "MonthInput",
    "WeekInput",
    "TimeInput",
    "DateTimeLocalInput",
    "NumberInput",
    "RangeInput",
    "ColorInput",
]


@attrs.define
class SearchInput(InputBase):
    """
    Renders an input with type "search".
    """

    input_type = "search"
    validation_attrs = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    }


@attrs.define
class TelInput(InputBase):
    """
    Renders an input with type "tel".
    """

    input_type = "tel"
    validation_attrs = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    }


@attrs.define
class URLInput(InputBase):
    """
    Renders an input with type "url".
    """

    input_type = "url"
    validation_attrs = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    }


@attrs.define
class EmailInput(InputBase):
    """
    Renders an input with type "email".
    """

    input_type = "email"
    validation_attrs = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    }


@attrs.define
class DateTimeInput(InputBase):
    """
    Renders an input with type "datetime".
    """

    input_type = "datetime"
    validation_attrs = {"required", "disabled", "readonly", "max", "min", "step"}


@attrs.define
class DateInput(InputBase):
    """
    Renders an input with type "date".
    """

    input_type = "date"
    validation_attrs = {"required", "disabled", "readonly", "max", "min", "step"}


@attrs.define
class MonthInput(InputBase):
    """
    Renders an input with type "month".
    """

    input_type = "month"
    validation_attrs = {"required", "disabled", "readonly", "max", "min", "step"}


@attrs.define
class WeekInput(InputBase):
    """
    Renders an input with type "week".
    """

    input_type = "week"
    validation_attrs = {"required", "disabled", "readonly", "max", "min", "step"}


@attrs.define
class TimeInput(InputBase):
    """
    Renders an input with type "time".
    """

    input_type = "time"
    validation_attrs = {"required", "disabled", "readonly", "max", "min", "step"}


@attrs.define
class DateTimeLocalInput(InputBase):
    """
    Renders an input with type "datetime-local".
    """

    input_type = "datetime-local"
    validation_attrs = {"required", "disabled", "readonly", "max", "min", "step"}


@attrs.define
class NumberInput(InputBase):
    """
    Renders an input with type "number".
    """

    step: int | None = None
    min: int | None = None
    max: int | None = None

    input_type = "number"
    validation_attrs = {"required", "disabled", "readonly", "max", "min", "step"}

    def __form_tag__(self, field: Field, **kwargs: Any) -> html_tag:
        if self.step is not None:
            kwargs.setdefault("step", self.step)
        if self.min is not None:
            kwargs.setdefault("min", self.min)
        if self.max is not None:
            kwargs.setdefault("max", self.max)
        return super().__form_tag__(field, **kwargs)


@attrs.define
class RangeInput(InputBase):
    """
    Renders an input with type "range".
    """

    step: int | None = None
    min: int | None = None
    max: int | None = None

    input_type = "range"
    validation_attrs = {"disabled", "max", "min", "step"}

    def __form_tag__(self, field: Field, **kwargs: Any) -> html_tag:
        if self.step is not None:
            kwargs.setdefault("step", self.step)
        if self.min is not None:
            kwargs.setdefault("min", self.min)
        if self.max is not None:
            kwargs.setdefault("max", self.max)
        return super().__form_tag__(field, **kwargs)


@attrs.define
class ColorInput(InputBase):
    """
    Renders an input with type "color".
    """

    tag = Tag(input, classes={"form-control-color"})

    input_type = "color"
    validation_attrs = {"disabled"}
