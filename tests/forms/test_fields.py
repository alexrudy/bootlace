import enum

import pytest
from wtforms import Form
from wtforms.validators import ValidationError

from bootlace.forms import fields


def test_enum_field() -> None:
    class TestEnum(enum.Enum):
        FOO = "foo"
        BAR = "bar"

    class TestForm(Form):
        field = fields.EnumField(enum=TestEnum)

    form = TestForm()

    assert form.field.choices == [("FOO", "Foo"), ("BAR", "Bar")]

    form.field.data = TestEnum.FOO

    assert form.field._value() == "FOO"

    form.field.data = None

    assert form.field._value() == ""

    assert form.field._coerce("FOO") == TestEnum.FOO
    assert form.field._coerce(TestEnum.FOO) == TestEnum.FOO


def test_markdown_field() -> None:
    class TestForm(Form):
        field = fields.MarkdownField()

    form = TestForm()

    form.field.data = "Hello\n\nWorld\n\nLong Paragaph\nHere"

    assert form.field._value() == "Hello\n\nWorld\n\nLong Paragaph Here"

    form.field.data = None

    assert form.field._value() == ""


def test_known_mime_type() -> None:
    validator = fields.KnownMIMEType()

    class TestForm(Form):
        field = fields.StringField(validators=[validator])  # type: ignore[attr-defined]

    form = TestForm()
    form.field.data = "text/plain"

    validator(form, form.field)

    form.field.data = "application/unknown"
    with pytest.raises(ValidationError):
        validator(form, form.field)

    form.field.data = "application/unknown"
    with pytest.raises(ValidationError) as exc_info:
        fields.KnownMIMEType("Custom message")(form, form.field)
    assert str(exc_info.value) == "Custom message"
