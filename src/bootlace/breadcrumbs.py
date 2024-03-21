from collections.abc import Callable
from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any
from typing import Protocol
from typing import TypeVar

import attrs
from dominate import tags
from dominate.util import text
from flask import Blueprint
from flask import current_app
from flask import Flask
from flask import request
from flask import url_for
from werkzeug.local import LocalProxy

from .util import as_tag
from .util import is_active_endpoint


class Named(Protocol):

    __name__: str


V = TypeVar("V", bound=Named)

EXTENSION_KEY: str = "bootlace.breadcrumbs"
DIVIDER_SETTING: str = "BOOTLACE_BREADCRUMBS_DIVIDER"


def endpoint_name(instance: object, attribute: attrs.Attribute, value: str) -> None:
    if "." in value:
        raise ValueError("Endpoint names cannot contain dots")


@attrs.define(frozen=True, init=False)
class KeywordArguments(Mapping[str, Any]):

    _arguments: frozenset[tuple[str, Any]]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        arguments = frozenset(dict(*args, **kwargs).items())
        object.__setattr__(self, "_arguments", arguments)

    def as_dict(self) -> dict[str, Any]:
        return dict(self._arguments)

    def __getitem__(self, __key: str) -> Any:
        return self.as_dict()[__key]

    def __iter__(self) -> Iterator[str]:
        return iter((key for key, _ in self._arguments))

    def __len__(self) -> int:
        return len(self._arguments)

    def __repr__(self) -> str:
        return f"KeywordArguments({self.as_dict()!r})"


@attrs.define(frozen=True, repr=False)
class Endpoint:
    """An endpoint for a breadcrumb, as captured at registration"""

    context: None | Blueprint
    name: str = attrs.field(validator=endpoint_name)
    url_kwargs: KeywordArguments = attrs.field(factory=lambda: KeywordArguments(), converter=KeywordArguments)
    ignore_query: bool = True

    @property
    def url(self) -> str:

        if isinstance(self.context, Blueprint):
            name = f"{self.context.name}.{self.name}"
            return url_for(name, **self.url_kwargs)

        return url_for(self.name, **self.url_kwargs)

    @property
    def active(self) -> bool:
        return is_active_endpoint(self.name, self.url_kwargs, self.ignore_query)

    def __repr__(self) -> str:
        parts = []
        if self.context is not None:
            parts.append(f"{self.context.name:s}.{self.name:s}")
        else:
            parts.append(f"{self.name:s}")

        if self.url_kwargs:
            parts.append(f", {self.url_kwargs!r}")

        if not self.ignore_query:
            parts.append(", ignore_query=False")

        statement = ", ".join(parts)
        return f"Endpoint({statement})"


@attrs.define
class Breadcrumb:
    """A single breadcrumb"""

    title: str
    link: Endpoint

    @property
    def active(self) -> bool:
        return self.link.active

    @property
    def url(self) -> str:
        return self.link.url

    def __tag__(self) -> tags.html_tag:
        if self.active:
            return text(self.title)

        return tags.a(self.title, href=self.url)


@attrs.define
class Breadcrumbs:
    """The trail of breadcrumbs"""

    crumbs: list[Breadcrumb] = attrs.field(factory=list)
    divider: str = attrs.field(default=">")

    def __iter__(self) -> Iterator[Breadcrumb]:
        return iter(self.crumbs)

    def __len__(self) -> int:
        return len(self.crumbs)

    def __getitem__(self, index: int) -> Breadcrumb:
        return self.crumbs[index]

    def push(self, crumb: Breadcrumb) -> None:
        self.crumbs.insert(0, crumb)

    def __tag__(self) -> tags.html_tag:
        if not self.crumbs:
            return text("")

        nav = tags.nav(aria_label="breadcrumb")
        if self.divider != "/":
            nav["style"] = f"--breadcrumb-divider: '{self.divider:s}';"  # noqa: B907

        ol = tags.ol(cls="breadcrumb")
        for crumb in self:
            item = tags.li(as_tag(crumb), cls="breadcrumb-item")
            if crumb.active:
                item["aria-current"] = "page"
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
        app.config.setdefault(DIVIDER_SETTING, ">")
        app.extensions[EXTENSION_KEY] = self

    def register(
        self, context: Flask | Blueprint | None, parent: str | Endpoint | None, title: str
    ) -> Callable[[V], V]:
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
