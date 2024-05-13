import warnings
from typing import Any
from typing import Self

import attrs
from dominate import tags

from .core import NavAlignment
from .core import NavStyle
from .core import SubGroup
from bootlace.util import as_tag
from bootlace.util import BootlaceWarning
from bootlace.util import ids as element_id
from bootlace.util import Tag


@attrs.define
class Nav(SubGroup):
    """A navigation bar"""

    #: The ID of the nav
    id: str = attrs.field(factory=element_id.factory("nav"))

    #: The style of the nav
    style: NavStyle = NavStyle.PLAIN

    #: The alignment of the elments in the nav
    alignment: NavAlignment = NavAlignment.DEFAULT

    ul: Tag = Tag(tags.ul, classes={"nav"})
    li: Tag = Tag(tags.li, classes={"nav-item"})

    def serialize(self) -> dict[str, Any]:
        data = super().serialize()
        data["style"] = self.style.name
        data["alignment"] = self.alignment.name
        return data

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> Self:
        data["style"] = NavStyle[data["style"]]
        data["alignment"] = NavAlignment[data["alignment"]]
        return super().deserialize(data)

    def __tag__(self) -> tags.html_tag:
        active_endpoint = next((item for item in self.items if item.active), None)
        ul = self.ul(id=self.id)

        if (style := self.style.value) != "":
            ul.classes.add(style)

        if (alignment := self.alignment.value) != "":
            ul.classes.add(alignment)

        if (link := getattr(active_endpoint, "link", None)) is not None:
            if (endpoint := getattr(link, "endpoint", None)) is not None:
                ul["data-endpoint"] = endpoint

        for item in self.items:
            ul.add(self.li(as_tag(item), __pretty=False))

        return ul


@attrs.define
class Dropdown(SubGroup):
    """A dropdown menu in the nav bar"""

    #: The title of the dropdown
    title: str = attrs.field(kw_only=True)

    #: The ID of the dropdown
    id: str = attrs.field(factory=element_id.factory("bs-dropdown"))

    dropdown: Tag = Tag(tags.div, classes={"dropdown"})
    ul: Tag = Tag(tags.ul, classes={"dropdown-menu"})
    li: Tag = Tag(tags.li)
    toggle: Tag = Tag(tags.a, classes={"nav-link", "dropdown-toggle"}, attributes={"role": "button"})

    def __tag__(self) -> tags.html_tag:
        div = self.dropdown()
        a = self.toggle(
            self.title,
            href="#",
            id=self.id,
        )
        a.aria["expanded"] = "false"
        a.data["bs-toggle"] = "dropdown"
        div.add(a)

        menu = self.ul()
        menu.aria["labelledby"] = self.id
        for item in self.items:
            tag = as_tag(item)
            if isinstance(tag, tags.html_tag):
                tag.classes.remove("nav-link")
                if not any(cls.startswith("dropdown-") for cls in tag.classes):
                    tag.classes.add("dropdown-item")
            else:
                warnings.warn(
                    BootlaceWarning(f"Item {item!r} is not an html tag, may not display properly"), stacklevel=2
                )
            menu.add(self.li(tag, __pretty=False))
        div.add(menu)
        return div
