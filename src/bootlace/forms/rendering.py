from typing import Any

from markupsafe import Markup
from wtforms import widgets as wt_widgets
from wtforms.fields import Field
from wtforms.meta import DefaultMeta

from . import widgets as bl_widgets


class BootlaceMeta(DefaultMeta):
    WIDGET_MAP = {getattr(wt_widgets, name): getattr(bl_widgets, name) for name in bl_widgets.__all__}

    def render_field(self, field: Field, render_kw: Any) -> Markup:
        cls = self.WIDGET_MAP[field.widget.__class__]
        widget = cls()
        return widget(field, render_kw)
