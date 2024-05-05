from typing import Any

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag
from dominate.util import container

from .core import Link
from .core import NavElement
from .core import SubGroup
from .nav import Nav
from bootlace.size import SizeClass
from bootlace.style import ColorClass
from bootlace.util import as_tag
from bootlace.util import ids as element_id


@attrs.define
class NavBar(NavElement):
    """A navigation bar, typically at the top of the page

    This is usually the primary navigation for a site.
    """

    #: The ID of the navbar
    id: str = attrs.field(factory=element_id.factory("navbar"))

    #: The elements in the navbar
    items: list[NavElement] = attrs.field(factory=list)

    #: The size of the navbar, if any, used to select when it
    #: should expand or collapse
    expand: SizeClass | None = SizeClass.LARGE

    #: The color of the navbar, if using a bootstrap color class
    color: ColorClass | None = ColorClass.TERTIARY

    #: Whether the navbar should be fluid (e.g. full width)
    fluid: bool = True

    def serialize(self) -> dict[str, Any]:
        data = super().serialize()
        data["items"] = [item.serialize() for item in self.items]
        data["expand"] = self.expand.value if self.expand else None
        data["color"] = self.color.value if self.color else None
        return data

    @classmethod
    def deserialize(cls, data: dict[str, Any]) -> NavElement:
        data["items"] = [NavElement.deserialize(item) for item in data["items"]]
        data["expand"] = SizeClass(data["expand"]) if data["expand"] else None
        data["color"] = ColorClass(data["color"]) if data["color"] else None
        return cls(**data)

    def __tag__(self) -> tags.html_tag:
        nav = tags.nav(cls="navbar")
        if self.expand:
            nav.classes.add(self.expand.add_to_class("navbar-expand"))
        if self.color:
            nav.classes.add(self.color.add_to_class("bg-body"))

        container = tags.div()
        if self.fluid:
            container.classes.add("container-fluid")
        else:
            container.classes.add("container")

        nav.add(container)

        for item in self.items:
            container.add(as_tag(item))

        return nav


@attrs.define
class Brand(Link):
    """The brand for the navbar, typically the site's logo or name

    You can pass :class:`~bootlace.links.Link` or :class:`~bootlace.links.View`
    as the source link, and
    """

    #: The ID of the brand
    id: str = attrs.field(factory=element_id.factory("navbar-brand"))

    def __tag__(self) -> dom_tag:
        a = as_tag(self.link)
        a["class"] = "navbar-brand"
        a["id"] = self.id
        return self.element_state(a)


@attrs.define
class NavBarCollapse(SubGroup):
    """A collection of nav elements that can be collapsed"""

    id: str = attrs.field(factory=element_id.factory("navbar-collapse"))

    def __tag__(self) -> dom_tag:
        button = tags.button(
            type="button",
            cls="navbar-toggler",
            data_bs_toggle="collapse",
            data_bs_target=f"#{self.id}",
            aria_controls=f"{self.id}",
            aria_expanded="false",
            aria_label="Toggle navigation",
        )
        button.add(tags.span(cls="navbar-toggler-icon"))
        div = tags.div(cls="collapse navbar-collapse", id=self.id)
        for item in self.items:
            div.add(as_tag(item))
        return container(button, div)


@attrs.define
class NavBarNav(Nav):
    """Primary grouping of nav elements in the navbar"""

    id: str = attrs.field(factory=element_id.factory("navbar-nav"))

    def __tag__(self) -> tags.html_tag:
        ul = tags.ul(cls="navbar-nav", id=self.id)
        for item in self.items:
            ul.add(tags.li(as_tag(item), cls="nav-item", __pretty=False))
        return ul


@attrs.define
class NavBarSearch(NavElement):
    """A search bar for the navbar"""

    id: str = attrs.field(factory=element_id.factory("navbar-search"))

    placeholder: str = "Search"
    action: str = "#"
    method: str = "GET"
    button: str | None = None

    def __tag__(self) -> dom_tag:
        form = tags.form(id=self.id)
        form.classes.add("d-flex")
        form["role"] = "search"

        input = tags.input_(
            type="search",
            cls="form-control me-2",
            placeholder=self.placeholder,
            aria_label=self.placeholder,
        )
        form.add(input)
        form.add(tags.button(self.button or self.placeholder, cls="btn btn-success", type="submit"))
        return self.element_state(form)
