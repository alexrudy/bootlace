from typing import Any

import attrs
from dominate import tags
from wtforms.fields import Field
from .core import Widget
from bootlace.util import Tag

@attrs.define
class Switch(Widget):
    div: Tag = Tag(tags.div, classes={"form-check", "form-switch"})
    input: Tag = Tag(tags.input_, classes={"form-check-input"}, attributes={
        "type": "checkbox",
        "role": "switch"
    })
    label: Tag = Tag(tags.label, classes={"form-check-label"})

    def __form_tag__(self, field: Field, **kwargs: Any) -> tags.html_tag:
        if getattr(field, "checked", field.data):
            kwargs["checked"] = True

        div = self.div()
        div.add(self.input(**kwargs))
        label = div.add(self.label(field.label.text))
        label["for"] = field.id
        return div
