from typing import Iterator
from collections.abc import MutableMapping

from .dom_tag import dom_tag

class Classes:
    def __contains__(self, cls: str) -> bool: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[str]: ...
    def add(self, *classes: str) -> "html_tag": ...
    def remove(self, *classes: str) -> "html_tag": ...
    def swap(self, old: str, new: str) -> "html_tag": ...

class PrefixAccess(MutableMapping[str, str]):
    def __init__(self, prefix: str, instance: "html_tag") -> None: ...
    def __getitem__(self, key: str) -> str: ...
    def __setitem__(self, key: str, value: str) -> None: ...
    def __delitem__(self, key: str) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...

class html_tag(dom_tag):
    @property
    def classes(self) -> Classes: ...

    data: PrefixAccess
    aria: PrefixAccess
    hx: PrefixAccess

class a(html_tag): ...
class button(html_tag): ...
class div(html_tag): ...
class form(html_tag): ...
class hr(html_tag): ...
class img(html_tag): ...
class input_(html_tag): ...
class label(html_tag): ...
class li(html_tag): ...
class nav(html_tag): ...
class ol(html_tag): ...
class span(html_tag): ...
class table(html_tag): ...
class tbody(html_tag): ...
class td(html_tag): ...
class th(html_tag): ...
class thead(html_tag): ...
class tr(html_tag): ...
class ul(html_tag): ...
class comment(dom_tag): ...
class link(html_tag): ...
class script(html_tag): ...
class meta(html_tag): ...
