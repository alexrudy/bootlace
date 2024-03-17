from wtforms import Form
from wtforms.fields import BooleanField

from bootlace.forms import widgets
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
