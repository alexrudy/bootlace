import domilite.tags
import pytest
from attr import s
from werkzeug.datastructures import MultiDict
from wtforms import Field
from wtforms import FileField
from wtforms import Form
from wtforms import SelectField
from wtforms.fields import BooleanField
from wtforms.fields import StringField

from bootlace.forms import widgets
from bootlace.forms.widgets.core import InputBase
from bootlace.forms.widgets.core import Widget
from bootlace.testing import assert_same_html


class BaseField(Form):
    field = Field()


class SimpleForm(Form):
    string = StringField()


class FileForm(Form):
    files = FileField()


class SwitchForm(Form):
    toggle = BooleanField(widget=widgets.Switch())


class SelectForm(Form):
    select = SelectField(choices=[("a", "A"), ("b", "B"), ("c", "C")])


class SelectGrouped(Form):
    select = SelectField(
        choices={
            "letters": [("a", "A"), ("b", "B"), ("c", "C")],
            "numbers": [("1", "one"), ("2", "two"), ("3", "three")],
            "bool": [(True, "true"), (False, "false")],
        }
    )


def test_switch_widget() -> None:
    form = SwitchForm()

    expected = """
    <div class="form-check form-switch">
        <input class="form-check-input" id="widget" name="widget" type="checkbox" role="switch" value="y"></input>
        <label class="form-check-label" for="widget">Widget</label>
    </div>"""

    assert_same_html(expected, form.toggle())


def test_switch_widget_checked() -> None:
    form = SwitchForm(data={"widget": True})

    expected = """
    <div class="form-check form-switch">
        <input class="form-check-input" id="widget" name="widget" type="checkbox" role="switch" value="y" checked></input>
        <label class="form-check-label" for="widget">Widget</label>
    </div>"""

    assert_same_html(expected, form.toggle())

    form = SwitchForm()
    form.toggle.checked = True  # type: ignore
    assert_same_html(expected, form.toggle())


def find_input(tag: domilite.tags.html_tag) -> domilite.tags.html_tag:
    if tag.name == "input":
        return tag
    else:
        for child in tag.descendants():
            if child.name == "input":
                return child
        else:
            assert False, "Can't find input"  # noqa: B011


@pytest.mark.parametrize(
    "widget",
    [
        widgets.TextInput,
        widgets.PasswordInput,
        widgets.HiddenInput,
        widgets.FileInput,
        widgets.CheckboxInput,
        widgets.RadioInput,
        widgets.SubmitInput,
    ],
)
def test_input_widget(widget: type[InputBase]):
    form = SimpleForm()
    tags = widget().__form_tag__(form.string)
    input_tag = find_input(tags)

    assert input_tag.attributes["type"] == widget.input_type, (
        f"Expected type {widget.input_type!r} but got {input_tag['type']!r}"
    )
    assert input_tag.attributes["id"] == form.string.id, f"Expected id {form.string.id!r} but got {input_tag['id']!r}"


def test_text_input():
    form = SimpleForm(data={"string": "something"})
    tags = widgets.TextInput().__form_tag__(form.string)
    assert tags["value"] == "something"
    assert tags["id"] == form.string.id
    assert "form-control" in tags.classes


def test_password_widget():
    form = SimpleForm(data={"string": "something"})
    tags = widgets.PasswordInput(hide_value=True).__form_tag__(form.string)
    assert tags["value"] == ""

    tags = widgets.PasswordInput(hide_value=False).__form_tag__(form.string)
    assert tags["value"] == "something"


def test_widget_input_explicit():
    form = SimpleForm()
    tags = widgets.Input(input_type="text").__form_tag__(form.string)
    input_tag = find_input(tags)

    assert input_tag.attributes["type"] == widgets.TextInput.input_type, (
        f"Expected type {widgets.TextInput.input_type!r} but got {input_tag['type']!r}"
    )
    assert input_tag.attributes["id"] == form.string.id, f"Expected id {form.string.id!r} but got {input_tag['id']!r}"


def test_widget_input_missing():
    form = SimpleForm()
    with pytest.warns(UserWarning):
        tags = widgets.Input(input_type=None).__form_tag__(form.string)
    input_tag = find_input(tags)

    assert "type" not in input_tag.attributes, f"Expected no 'type' attribute but got {input_tag['type']!r}"
    assert input_tag.attributes["id"] == form.string.id, f"Expected id {form.string.id!r} but got {input_tag['id']!r}"


def test_widget_inputbase():
    form = SimpleForm()
    with pytest.warns(UserWarning):
        tags = widgets.core.InputBase().__form_tag__(form.string)
    input_tag = find_input(tags)

    assert "type" not in input_tag.attributes, f"Expected no 'type' attribute but got {input_tag['type']!r}"
    assert input_tag.attributes["id"] == form.string.id, f"Expected id {form.string.id!r} but got {input_tag['id']!r}"


class CustomField(Field):
    pass


class CustomFieldForm(Form):
    custom = CustomField()


def test_custom_field() -> None:
    form = CustomFieldForm(data={"custom": "custom value"})
    assert not hasattr(form.custom, "_value")

    widget = widgets.TextInput()
    assert widget.get_field_value(form.custom) == "custom value"


def test_custom_flags() -> None:
    form = SimpleForm()
    form.string.flags.readonly = True
    widget = widgets.TextInput()
    tags = widget.__form_tag__(form.string)

    assert tags["readonly"]


@pytest.mark.parametrize("widget", [widgets.CheckboxInput(), widgets.RadioInput()])
def test_checked_widgets(widget: Widget) -> None:
    form = SwitchForm(data={"toggle": True})

    assert form.toggle.data
    tags = widget.__form_tag__(form.toggle)
    print(tags)
    assert tags["checked"]

    form = SwitchForm(data={"toggle": False})
    tags = widget.__form_tag__(form.toggle)
    assert "checked" not in tags.attributes

    form.toggle.checked = True  # type: ignore
    tags = widget.__form_tag__(form.toggle)
    assert tags["checked"]


def test_file_multiple() -> None:
    form = FileForm()
    widget = widgets.FileInput()
    tags = widget.__form_tag__(form.files)

    assert "multiple" not in tags.attributes

    widget = widgets.FileInput(multiple=True)
    tags = widget.__form_tag__(form.files)
    assert tags["multiple"]


def test_text_area_escape() -> None:
    form = SimpleForm(data={"string": "<&>"})
    widget = widgets.TextArea()
    tags = widget.__form_tag__(form.string)
    assert tags["value"] == "&lt;&amp;&gt;"

    form = BaseField(data={"field": None})
    widget = widgets.TextArea()
    tags = widget.__form_tag__(form.field)
    assert "value" not in tags.attributes


def test_select_fields() -> None:
    form = SelectForm()
    widget = widgets.Select()
    tags = widget.__form_tag__(form.select)

    for child in tags.children:
        assert child.name == "option"


def test_select_widget_invalid_field() -> None:
    form = SimpleForm()
    widget = widgets.Select()

    with pytest.raises(TypeError):
        widget.__form_tag__(form.string)


def test_select_multiple() -> None:
    form = SelectForm()
    widget = widgets.Select(multiple=True)  # pyright: ignore

    tags = widget.__form_tag__(form.select)
    assert tags["multiple"]


def test_select_groups() -> None:
    form = SelectGrouped(MultiDict({"select": "a"}))
    widget = widgets.Select(multiple=True)  # pyright: ignore

    tag = widget.__form_tag__(form.select)
    for child in tag.children:
        assert isinstance(child, domilite.tags.html_tag)
        assert child.name == "optgroup"
        for opt in child.children:
            assert isinstance(opt, domilite.tags.html_tag)
            assert opt.name == "option"
            if opt.attributes.get('value', None) == "a":
                assert opt["selected"]

def test_number_input() -> None:

    form = SimpleForm()
    widget = widgets.NumberInput(min=2, max=5, step=1)
    tag = widget.__form_tag__(form.string)

    assert tag['min'] == 2
    assert tag['max'] == 5
    assert tag['step'] == 1
    assert tag['type'] == 'number'

    widget = widgets.NumberInput()
    tag = widget.__form_tag__(form.string)

    assert tag['type'] == 'number'
    assert 'min' not in tag.attributes
    assert 'max' not in tag.attributes
    assert 'step' not in tag.attributes

def test_range_input() -> None:

    form = SimpleForm()
    widget = widgets.RangeInput(min=2, max=5, step=1)
    tag = widget.__form_tag__(form.string)

    assert tag['min'] == 2
    assert tag['max'] == 5
    assert tag['step'] == 1
    assert tag['type'] == 'range'

    widget = widgets.RangeInput()
    tag = widget.__form_tag__(form.string)

    assert tag['type'] == 'range'
    assert 'min' not in tag.attributes
    assert 'max' not in tag.attributes
    assert 'step' not in tag.attributes
