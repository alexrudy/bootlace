from typing import Any

from dominate import tags
from wtforms.fields import Field

__all__ = ["Switch"]


class Switch:

    def __init__(self, **kwargs: Any) -> None:
        super().__init__()
        self.kwargs = kwargs

    def __call__(self, field: Field, **kwargs: Any) -> str:
        div = tags.div(cls="form-check form-switch")

        kwargs.setdefault("cls", "form-check-input")
        kwargs.setdefault("type", "checkbox")
        kwargs.setdefault("role", "switch")

        div.add(tags.input_(**kwargs))
        label = div.add(tags.label(field.label.text, cls="form-check-label"))
        label["for"] = field.id
        return div.render()
