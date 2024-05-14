import collections
import functools
import itertools
import warnings
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from collections.abc import Mapping
from collections.abc import MutableMapping
from collections.abc import MutableSet
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeAlias
from typing import TypeVar

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag
from dominate.util import container
from dominate.util import text
from flask import request
from markupsafe import Markup

T = TypeVar("T")

__all__ = [
    "BootlaceWarning",
    "Classes",
    "HtmlIDScope",
    "IntoTag",
    "MaybeTaggable",
    "Taggable",
    "Tag",
    "as_tag",
    "ids",
    "is_active_endpoint",
    "maybe",
    "render",
]


class BootlaceWarning(UserWarning):
    """A warning specific to Bootlace"""


def _monkey_patch_dominate() -> None:
    """Monkey patch the dominate tags to support class attribute manipulation"""
    tags.html_tag.classes = property(lambda self: Classes(self))  # type: ignore
    tags.html_tag.data = PrefixAccessor("data")  # type: ignore
    tags.html_tag.aria = PrefixAccessor("aria")  # type: ignore
    tags.html_tag.hx = PrefixAccessor("hx")  # type: ignore


class Taggable(Protocol):
    """Protocol for objects that can be converted to a tag."""

    def __tag__(self) -> dom_tag:
        """Convert the object to a dominate tag.

        This method gives objects control over how they are processed by :func:`as_tag`. It should return a
        :mod:`dominate` tag. If a taggable object contains other taggable objects, it should use :func:`as_tag` to
        convert them, and then apply any additional processing as necessary to the returned :class:`~dominate.html_tag`.

        :meta public:
        :returns: A :mod:`dominate` tag.
        """
        ...


#: A type that can be converted to a tag
IntoTag: TypeAlias = Taggable | dom_tag

#: A type that can be converted to a tag via :func:`as_tag`
MaybeTaggable: TypeAlias = IntoTag | str | Iterable[Taggable | dom_tag]


def as_tag(item: MaybeTaggable) -> dom_tag:
    """Convert an item to a dominate tag.

    :mod:`bootlace` uses :mod:`dominate` to render HTML. To do this, objects implement the :class:`Taggable` protocol,
    providing a ``__tag__`` dunder method. This method will also accept regular :mod:`dominate` tags, strings, and
    iterables of :class:`Taggable` objects. It will try to always return a :mod:`dominate` tag.

    To render taggable objects in a template, use :func:`render`, a convenience function that will convert the object
    to a :mod:`dominate` tag and then render it to a :class:`Markup` object for use in a template.

    Handling notes
    --------------

    When a string is passed in, it will be wrapped with :class:`dominate.util.text` to render a literal string as a
    tag. When an iterable of taggable items is passed, it is returned as a :class:`dominate.util.container`, which will
    render the tags in sequence.

    Unknown types are displayed using their string representation (by calling :class:`str` on them), along with a
    comment in the rendered HTML and a :class:`Bootlace` warning emitted.

    Arguments
    ---------

    :param item: The item to convert to :mod:`dominate` tags.
    :returns: A :mod:`dominate` tag.

    """

    if isinstance(item, tags.html_tag):
        return item
    if hasattr(item, "__tag__"):
        return item.__tag__()
    if isinstance(item, str):
        return text(item)
    if isinstance(item, Iterable):
        return container(*[as_tag(i) for i in item])

    warnings.warn(BootlaceWarning(f"Rendered type {item.__class__.__name__} not explicitly supported"), stacklevel=2)
    return container(text(str(item)), tags.comment(f"Rendered type {item.__class__.__name__} not supported"))


def render(item: MaybeTaggable) -> Markup:
    """Render an item to a Markup object.

    This function is a convenience wrapper around :func:`as_tag` and :meth:`dominate.tags.html_tag.render`. It will try
    to convert most objects to a :mod:`dominate` tag and then render it to a :class:`Markup` object which can be
    inserted into :mod:`jinja` templates.

    Arguments
    ---------
    :param item: The item to render. See :func:`as_tag` for more information.
    :returns: A :class:`Markup` object, suitable for inserting into a :mod:`jinja` template.

    """
    return Markup(as_tag(item).render())


class Classes(MutableSet[str]):
    """A helper for manipulating the class attribute on a tag."""

    def __init__(self, tag: tags.html_tag) -> None:
        self.tag = tag

    def __contains__(self, cls: object) -> bool:
        return cls in self.tag.attributes.get("class", "").split()

    def __iter__(self) -> Iterator[str]:
        return iter(self.tag.attributes.get("class", "").split())

    def __len__(self) -> int:
        return len(self.tag.attributes.get("class", "").split())

    def add(self, *classes: str) -> tags.html_tag:  # type: ignore[override]
        """Add classes to the tag."""
        current: list[str] = self.tag.attributes.get("class", "").split()
        for cls in classes:
            if cls not in current:
                current.append(cls)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag

    def remove(self, *classes: str) -> tags.html_tag:  # type: ignore[override]
        """Remove classes from the tag."""
        current: list[str] = self.tag.attributes.get("class", "").split()
        for cls in classes:
            if cls in current:
                current.remove(cls)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag

    def discard(self, value: str) -> None:
        """Remove a class if it exists."""
        self.remove(value)

    def swap(self, old: str, new: str) -> tags.html_tag:
        """Swap one class for another."""
        current: list[str] = self.tag.attributes.get("class", "").split()
        if old in current:
            current.remove(old)
        if new not in current:
            current.append(new)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag


@attrs.define
class PrefixAccessor:
    """A helper for accessing attributes with a prefix."""

    #: Attribute prefix
    prefix: str = attrs.field()

    def __get__(self, instance: tags.html_tag, owner: type[tags.html_tag]) -> "PrefixAccess":
        return PrefixAccess(self.prefix, instance)


@attrs.define
class PrefixAccess(MutableMapping[str, str]):

    #: Attribute prefix
    prefix: str = attrs.field()

    #: The tag to access
    tag: tags.html_tag = attrs.field()

    def __getitem__(self, name: str) -> str:
        return self.tag.attributes[f"{self.prefix}-{name}"]

    def __setitem__(self, name: str, value: str) -> None:
        self.tag.attributes[f"{self.prefix}-{name}"] = value

    def __delitem__(self, name: str) -> None:
        del self.tag.attributes[f"{self.prefix}-{name}"]

    def __iter__(self) -> Iterator[str]:
        for key in self.tag.attributes:
            if key.startswith(f"{self.prefix}-"):
                yield key[len(self.prefix) + 1 :]

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def set(self, name: str, value: str) -> tags.html_tag:
        """Set an attribute with the given name."""
        self[name] = value
        return self.tag

    def remove(self, name: str) -> tags.html_tag:
        """Remove an attribute with the given name."""
        del self[name]
        return self.tag


@attrs.define
class HtmlIDScope:
    """A helper for generating unique HTML IDs."""

    #: A mapping of scopes to counters
    scopes: collections.defaultdict[str, itertools.count] = attrs.field(
        factory=lambda: collections.defaultdict(itertools.count)
    )

    def __call__(self, scope: str) -> str:
        """Generate a unique ID for a given scope.

        Parameters
        ----------
        scope : str
            Scopes are used to group IDs together, e.g. items in a list, or a form and its fields.
        """
        counter = next(self.scopes[scope])
        if counter == 0:
            return scope
        return f"{scope}-{counter}"

    def factory(self, scope: str) -> functools.partial:
        """Create a factory function for generating IDs in a specific scope."""
        return functools.partial(self, scope)

    def reset(self) -> None:
        """Reset all ID scopes."""
        self.scopes.clear()


ids = HtmlIDScope()


def maybe(cls: type[T]) -> Callable[[str | T], T]:
    """Convert a string to a class instance if necessary."""

    def converter(value: str | T) -> T:
        if isinstance(value, str):
            return cls(value)  # type: ignore
        return value

    return converter


def is_active_endpoint(endpoint: str, url_kwargs: Mapping[str, Any], ignore_query: bool = True) -> bool:
    """Check if the current request is for the given endpoint and URL kwargs"""
    if request.endpoint != endpoint:
        return False

    if request.url_rule is None:  # pragma: no cover
        return False

    rule_url = request.url_rule.build(url_kwargs, append_unknown=not ignore_query)

    if rule_url is None:  # pragma: no cover
        return False

    _, url = rule_url

    return url == request.path


H = TypeVar("H", bound=tags.html_tag)


@attrs.define
class Tag(Generic[H]):
    """A helper for creating tags.

    Holds the tag type as well as attributes for the tag. This can be used
    by calling the instance as a function to create a tag, or by calling the
    :meth:`update` method to apply the attributes to an existing tag.
    """

    #: The tag type
    tag: type[H] = attrs.field()

    #: The classes to apply to the tag
    classes: set[str] = attrs.field(factory=set)

    #: The attributes to apply to the tag
    attributes: dict[str, str] = attrs.field(factory=dict)

    def __tag__(self) -> H:
        """Create a tag from the attributes and classes."""
        tag = self.tag(**self.attributes)
        tag.classes.add(*self.classes)
        return tag

    def __call__(self, *args: Any, **kwds: Any) -> H:
        """Create a tag from the attributes and classes.

        This method is a convenience wrapper around :meth:`__tag__` that allows
        the tag to be created with additional arguments and keyword arguments passed
        to the tag constructor.
        """
        tag = self.tag(*args, **{**self.attributes, **kwds})
        tag.classes.add(*self.classes)
        return tag

    def __setitem__(self, name: str, value: str) -> None:
        self.attributes[name] = value

    def __getitem__(self, name: str) -> str:
        return self.attributes[name]

    def update(self, tag: H) -> H:
        """Update the tag with the attributes and classes."""
        tag.classes.add(*self.classes)
        tag.attributes.update(self.attributes)
        return tag
