import attrs
from dominate import tags
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
    id: str = attrs.field(factory=element_id.factory("navbar"))
    items: list[NavElement] = attrs.field(factory=list)
    expand: SizeClass | None = SizeClass.LARGE
    color: ColorClass | None = ColorClass.TERTIARY
    fluid: bool = True

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
    id: str = attrs.field(factory=element_id.factory("navbar-brand"))

    def __tag__(self) -> tags.html_tag:
        a = as_tag(self.link)
        a["class"] = "navbar-brand"
        a["id"] = self.id
        return self.element_state(a)


@attrs.define
class NavBarCollapse(SubGroup):
    """A collection of nav elements that can be collapsed"""

    id: str = attrs.field(factory=element_id.factory("navbar-collapse"))

    def __tag__(self) -> tags.html_tag:
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

    def __tag__(self) -> tags.html_tag:
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
