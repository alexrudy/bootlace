import collections
import functools
import itertools
import warnings
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Iterator
from typing import Protocol
from typing import TypeVar

import attrs
from dominate import tags
from dominate.util import container
from dominate.util import text

T = TypeVar("T")


class BootlaceWarning(UserWarning):
    """A warning specific to Bootlace"""


def _monkey_patch_dominate() -> None:
    """Monkey patch the dominate tags to support class attribute manipulation"""
    tags.html_tag.classes = property(lambda self: Classes(self))


class Taggable(Protocol):
    def __tag__(self) -> tags.html_tag: ...


IntoTag = Taggable | tags.html_tag

MaybeTaggable = IntoTag | str | Iterable[Taggable | tags.html_tag]


def as_tag(item: Taggable) -> tags.html_tag:
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


def render(item: Taggable) -> str:
    return as_tag(item).render()


class Classes:
    def __init__(self, tag: tags.html_tag) -> None:
        self.tag = tag

    def __contains__(self, cls: str) -> bool:
        return cls in self.tag.attributes.get("class", "").split()

    def __iter__(self) -> Iterator[str]:
        return iter(self.tag.attributes.get("class", "").split())

    def add(self, *classes: str) -> tags.html_tag:
        current: list[str] = self.tag.attributes.get("class", "").split()
        for cls in classes:
            if cls not in current:
                current.append(cls)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag

    def remove(self, *classes: str) -> tags.html_tag:
        current: list[str] = self.tag.attributes.get("class", "").split()
        for cls in classes:
            if cls in current:
                current.remove(cls)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag

    def swap(self, old: str, new: str) -> tags.html_tag:
        current: list[str] = self.tag.attributes.get("class", "").split()
        if old in current:
            current.remove(old)
        if new not in current:
            current.append(new)
        self.tag.attributes["class"] = " ".join(current)
        return self.tag


@attrs.define
class HtmlIDScope:
    scopes: collections.defaultdict[str, itertools.count] = attrs.field(
        factory=lambda: collections.defaultdict(itertools.count)
    )

    def __call__(self, scope: str) -> str:
        counter = next(self.scopes[scope])
        if counter == 0:
            return scope
        return f"{scope}-{counter}"

    def factory(self, scope: str) -> functools.partial:
        return functools.partial(self, scope)


ids = HtmlIDScope()


def maybe(cls: type[T]) -> Callable[[str | T], T]:
    def converter(value: str | T) -> T:
        if isinstance(value, str):
            return cls(value)  # type: ignore
        return value

    return converter
