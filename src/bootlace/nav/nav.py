import attrs
from dominate import tags

from bootlace.util import ids as element_id
from bootlace.util import as_tag
from .core import NavAlignment, NavStyle, SubGroup


@attrs.define
class Nav(SubGroup):
    id: str = attrs.field(factory=element_id.factory("nav"))
    style: NavStyle = NavStyle.PLAIN
    alignment: NavAlignment = NavAlignment.DEFAULT

    def __tag__(self) -> tags.html_tag:
        active_endpoint = next((item for item in self.items if item.active), None)
        ul = tags.ul(cls="nav", id=self.id)

        if (style := self.style.value) != "":
            ul.classes.add(style)

        if (alignment := self.alignment.value) != "":
            ul.classes.add(alignment)

        if (link := getattr(active_endpoint, "link", None)) is not None:
            if (endpoint := getattr(link, "endpoint", None)) is not None:
                ul["data-endpoint"] = endpoint

        for item in self.items:
            ul.add(tags.li(as_tag(item), cls="nav-item", __pretty=False))

        return ul


@attrs.define
class Dropdown(SubGroup):
    title: str = attrs.field(kw_only=True)
    id: str = attrs.field(factory=element_id.factory("bs-dropdown"))

    def __tag__(self) -> tags.html_tag:
        div = tags.div(cls="dropdown")
        a = tags.a(
            self.title,
            href="#",
            cls="nav-link dropdown-toggle",
            role="button",
            id=self.id,
            aria_expanded="false",
            data_bs_toggle="dropdown",
        )
        div.add(a)
        menu = tags.ul(cls="dropdown-menu", aria_labelledby=self.id)
        for item in self.items:
            tag = as_tag(item)
            tag.classes.remove("nav-link")
            if not any(cls.startswith("dropdown-") for cls in tag.classes):
                tag.classes.add("dropdown-item")
            menu.add(tags.li(tag, __pretty=False))
        div.add(menu)
        return div
