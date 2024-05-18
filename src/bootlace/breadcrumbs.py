from collections.abc import Callable
from collections.abc import Iterator
from typing import Protocol
from typing import TypeVar

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag
from dominate.util import text
from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import request
from werkzeug.local import LocalProxy

from .util import as_tag
from .util import Tag
from bootlace.endpoint import Endpoint

__all__ = [
    "breadcrumbs",
    "Breadcrumb",
    "Breadcrumbs",
    "BreadcrumbEntry",
    "BreadcrumbExtension",
]


class Named(Protocol):

    __name__: str


V = TypeVar("V", bound=Named)

EXTENSION_KEY: str = "bootlace.breadcrumbs"
DIVIDER_SETTING: str = "BOOTLACE_BREADCRUMBS_DIVIDER"


@attrs.define
class Breadcrumb:
    """A single breadcrumb, representing a single, possibly active, endpoint"""

    #: The title of the breadcrumb, displayed in text
    title: str

    #: The endpoint for the breadcrumb
    link: Endpoint

    a: Tag = Tag(tags.a)

    @property
    def active(self) -> bool:
        """Whether the breadcrumb is the active view"""
        return self.link.active

    @property
    def url(self) -> str:
        """The URL for the breadcrumb"""
        return self.link.url

    def __tag__(self) -> dom_tag:
        if self.active:
            return text(self.title)

        return self.a(self.title, href=self.url)


@attrs.define
class Breadcrumbs:
    """The trail of breadcrumbs

    Supports the :func:`as_tag` protocol to render the breadcrumbs as HTML"""

    #: The list of breadcrumbs, in order from broadest to most specific
    crumbs: list[Breadcrumb] = attrs.field(factory=list)

    #: The divider to use between breadcrumbs
    divider: str = attrs.field(default=">")

    nav: Tag = Tag(tags.nav)
    ol: Tag = Tag(tags.ol, classes={"breadcrumb"})
    li: Tag = Tag(tags.li, classes={"breadcrumb-item"})

    def __iter__(self) -> Iterator[Breadcrumb]:
        return iter(self.crumbs)

    def __len__(self) -> int:
        return len(self.crumbs)

    def __getitem__(self, index: int) -> Breadcrumb:
        return self.crumbs[index]

    def push(self, crumb: Breadcrumb) -> None:
        """Add a new crumb to the beginning of the list"""
        self.crumbs.insert(0, crumb)

    def __tag__(self) -> dom_tag:
        if not self.crumbs:
            return text("")

        nav = self.nav()
        nav.aria["label"] = "breadcrumb"

        if self.divider != "/":
            nav["style"] = f"--breadcrumb-divider: '{self.divider:s}';"  # noqa: B907

        ol = self.ol()
        for crumb in self:
            item = self.li(as_tag(crumb))
            if crumb.active:
                item.aria["current"] = "page"
                item.classes.add("active")
            ol.add(item)
        nav.add(ol)
        return nav


@attrs.define
class BreadcrumbEntry:
    """A single entry in the breadcrumbs datastructure"""

    title: str
    parent: Endpoint | None


@attrs.define(init=False)
class BreadcrumbExtension:
    """An extension for breadcrumbs"""

    tree: dict[Endpoint, BreadcrumbEntry] = attrs.field(factory=dict)

    def __init__(self, app: Flask | None = None) -> None:
        self.tree = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Set up the extension on the app"""
        app.config.setdefault(DIVIDER_SETTING, ">")
        app.extensions[EXTENSION_KEY] = self

    def register(
        self, context: Flask | Blueprint | None, parent: str | Endpoint | None, title: str
    ) -> Callable[[V], V]:
        """Register a breadcrumb for a view

        :param context: The context for the view, if any.
            For a blueprint, this is the blueprint object. For a view on the root app,
            this ie either the root app or None.
        :param parent: The parent for the breadcrumb. This can be a string, an endpoint, or None.
            If a string, it is the name of the parent endpoint. If an endpoint, it is the parent endpoint.
            If None, there is no parent, and this is a root item.
        :param title: The title of the breadcrumb

        :returns: A decorator that can be used to register the view, which will return the view unchanged.
        """
        if isinstance(context, Flask):
            context = None

        parent_link: Endpoint | None = None
        if isinstance(parent, str):
            if parent.startswith("."):
                if context is None:
                    raise ValueError("Cannot use relative endpoint without a context")
                parent_link = Endpoint(name=parent.lstrip("."), context=context)
            else:
                parent_link = Endpoint(name=parent, context=None)
        else:
            parent_link = parent

        def decorator(view: V) -> V:
            nonlocal parent_link
            link = Endpoint(name=view.__name__, context=context)

            if link == parent_link:
                raise ValueError("A breadcrumb cannot be its own parent")

            self.tree[link] = BreadcrumbEntry(title=title, parent=parent_link)
            return view

        return decorator

    @property
    def divider(self) -> str:
        """The divider to use between breadcrumbs"""
        return current_app.config[DIVIDER_SETTING]

    def _current_context(self) -> Blueprint | None:
        if request.blueprint:
            return current_app.blueprints[request.blueprint]  # type: ignore
        return None

    def _current_endpoint(self) -> Endpoint | None:
        context = self._current_context()
        if not request.endpoint:  # pragma: no cover
            return None

        name = request.endpoint.split(".")[-1]

        return Endpoint(name=name, context=context)

    def get(self) -> Breadcrumbs:
        """Get the :class:`Breadcrumbs` for the current request"""
        endpoint = self._current_endpoint()
        crumbs = Breadcrumbs(divider=self.divider)
        if not endpoint:  # pragma: no cover
            return crumbs

        current = self.tree.get(endpoint)
        while current:
            crumbs.push(Breadcrumb(title=current.title, link=endpoint))
            if not current.parent:
                break
            endpoint = current.parent
            current = self.tree.get(endpoint)

        return crumbs


breadcrumbs: BreadcrumbExtension = LocalProxy(lambda: current_app.extensions[EXTENSION_KEY])  # type: ignore
