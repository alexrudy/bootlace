import pytest
from wtforms import Form
from wtforms.fields import BooleanField, StringField
from dominate import tags

from bootlace.forms import widgets
from bootlace.forms.widgets.core import InputBase
from bootlace.testing import assert_same_html


def test_switch_widget() -> None:

    class TestForm(Form):
        widget = BooleanField(widget=widgets.Switch())

    form = TestForm()

    expected = """
    <div class="form-check form-switch">
        <input class="form-check-input" id="widget" name="widget" type="checkbox" role="switch" value="y"></input>
        <label class="form-check-label" for="widget">Widget</label>
    </div>"""

    assert_same_html(expected, form.widget())

def test_switch_widget_checked() -> None:
    class TestForm(Form):
        widget = BooleanField(widget=widgets.Switch())

    form = TestForm(data={'widget': True})

    expected = """
    <div class="form-check form-switch">
        <input class="form-check-input" id="widget" name="widget" type="checkbox" role="switch" value="y" checked></input>
        <label class="form-check-label" for="widget">Widget</label>
    </div>"""

    assert_same_html(expected, form.widget())


@pytest.mark.parametrize("widget", [widgets.TextInput, widgets.PasswordInput, widgets.HiddenInput, widgets.FileInput, widgets.CheckboxInput, widgets.RadioInput, widgets.SubmitInput])
def test_widget(widget: type[InputBase]):
    class TestForm(Form):
        input = StringField()

    form =TestForm()
    tags = widget().__form_tag__(form.input)
    if type(tags).__name__ == 'input_':
        input_tag = tags
    else:
        [input_tag] = tags.get('input_')

    assert input_tag.attributes['type'] == widget.input_type, f"Expected type '{widget.input_type}' but got '{input_tag['type']}'"
    assert input_tag.attributes['id'] == form.input.id, f"Expected id '{form.input.id}' but got '{input_tag['id']}'"

def test_widget_input_explicit():
    class TestForm(Form):
        input = StringField()

    form = TestForm()
    tags = widgets.Input(input_type='text').__form_tag__(form.input)
    if type(tags).__name__ == 'input_':
        input_tag = tags
    else:
        [input_tag] = tags.get('input_')

    assert input_tag.attributes['type'] == widgets.TextInput.input_type, f"Expected type '{widgets.TextInput.input_type}' but got '{input_tag['type']}'"
    assert input_tag.attributes['id'] == form.input.id, f"Expected id '{form.input.id}' but got '{input_tag['id']}'"

def test_widget_input_missing():
    class TestForm(Form):
        input = StringField()

    form = TestForm()
    with pytest.warns(UserWarning):
        tags = widgets.Input(input_type=None).__form_tag__(form.input)
    if type(tags).__name__ == 'input_':
        input_tag = tags
    else:
        [input_tag] = tags.get('input_')

    assert 'type' not in input_tag.attributes, f"Expected no 'type' attribute but got '{input_tag['type']}'"
    assert input_tag.attributes['id'] == form.input.id, f"Expected id '{form.input.id}' but got '{input_tag['id']}'"

def test_widget_inputbase():
    class TestForm(Form):
        input = StringField()

    form = TestForm()
    with pytest.warns(UserWarning):
        tags = widgets.core.InputBase().__form_tag__(form.input)
    if type(tags).__name__ == 'input_':
        input_tag = tags
    else:
        [input_tag] = tags.get('input_')

    assert 'type' not in input_tag.attributes, f"Expected no 'type' attribute but got '{input_tag['type']}'"
    assert input_tag.attributes['id'] == form.input.id, f"Expected id '{form.input.id}' but got '{input_tag['id']}'"
