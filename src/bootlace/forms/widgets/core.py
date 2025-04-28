import warnings
from typing import Any
from typing import ClassVar

import attrs
from domilite import tags
from markupsafe import Markup
from markupsafe import escape
from wtforms.fields import Field

from bootlace.util import Tag
from bootlace.util import render

__all__ = [
    "Widget",
    "Input",
    "TextInput",
    "PasswordInput",
    "HiddenInput",
    "CheckboxInput",
    "RadioInput",
    "FileInput",
    "SubmitInput",
    "TextArea",
]


@attrs.define
class Widget:
    classes: ClassVar[set[str]]
    tag: ClassVar[Tag]
    validation_attrs: ClassVar[set[str]] = set()

    def get_field_value(self, field: Field) -> Any:
        if (get_value := getattr(field, "_value", None)) is not None:
            return get_value()
        return field.data

    def prepare_attributes(self, field: Field, kwargs: dict[str, Any]) -> dict[str, Any]:
        return kwargs

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        kwargs.setdefault("id", field.id)
        if "value" not in kwargs and ((value := self.get_field_value(field)) is not None):
            kwargs["value"] = value

        flags = getattr(field, "flags", object())
        for k in dir(flags):
            if k in self.validation_attrs and k not in kwargs:
                kwargs[k] = getattr(flags, k)

        kwargs = self.prepare_attributes(field, kwargs)
        return self.tag(**kwargs)

    def __call__(self, field: Field, **kwargs: Any) -> Markup:
        return render(self.__form_tag__(field, **kwargs))


@attrs.define
class InputBase(Widget):
    """A base input widget"""

    input_type: ClassVar[str | None] = None
    tag = Tag(tags.input, classes={"form-control"})

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        if self.input_type is not None:
            kwargs.setdefault("type", self.input_type)
        else:
            warnings.warn("Input type not specified", stacklevel=2)
        return super().__form_tag__(field, **kwargs)


@attrs.define
class Input(Widget):
    """A base input widget"""

    input_type: str | None = None
    tag = Tag(tags.input, classes={"form-control"})

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        if self.input_type is not None:
            kwargs.setdefault("type", self.input_type)
        else:
            warnings.warn("Input type not specified", stacklevel=2)
        return super().__form_tag__(field, **kwargs)


@attrs.define
class TextInput(InputBase):
    """Render a single-line text input"""

    input_type = "text"
    validation_attrs = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    }


@attrs.define
class PasswordInput(InputBase):
    hide_value: bool = True

    input_type = "password"
    validation_attrs = {
        "required",
        "disabled",
        "readonly",
        "maxlength",
        "minlength",
        "pattern",
    }

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        if self.hide_value:
            kwargs["value"] = ""
        return super().__form_tag__(field, **kwargs)


@attrs.define
class HiddenInput(InputBase):
    input_type = "hidden"
    validation_attrs = {"disabled"}


@attrs.define
class CheckboxInput(InputBase):
    input_type = "checkbox"
    validation_attrs = {"required", "disabled"}

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        if getattr(field, "checked", field.data):
            kwargs["checked"] = True
        return super().__form_tag__(field, **kwargs)


@attrs.define
class RadioInput(InputBase):
    input_type = "radio"
    validation_attrs = {"required", "disabled"}

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        if getattr(field, "checked", field.data):
            kwargs["checked"] = True
        return super().__form_tag__(field, **kwargs)


@attrs.define
class FileInput(InputBase):
    multiple: bool = False

    input_type = "file"
    validation_attrs = {"required", "disabled", "accept"}

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        kwargs["value"] = False
        if self.multiple:
            kwargs["multiple"] = True

        return super().__form_tag__(field, **kwargs)


@attrs.define
class SubmitInput(InputBase):
    input_type = "submit"
    validation_attrs = {"required", "disabled"}

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        kwargs.setdefault("value", field.label.text)
        return super().__form_tag__(field, **kwargs)


@attrs.define
class TextArea(Widget):
    validation_attrs = {"required", "disabled", "readonly", "maxlength", "minlength"}

    tag = Tag(tags.textarea, classes={"form-control"})

    def get_field_value(self, field: Field) -> Any:
        value = super().get_field_value(field)
        if value is not None:
            return escape(value)
        return value
