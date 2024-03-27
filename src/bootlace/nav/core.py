import enum
import warnings
from typing import Any

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag

from bootlace import links
from bootlace.image import Image
from bootlace.util import as_tag
from bootlace.util import BootlaceWarning
from bootlace.util import ids as element_id


class NavStyle(enum.Enum):
    """Styles for the nav element"""

    PLAIN = ""
    TABS = "nav-tabs"
    PILLS = "nav-pills"
    UNDERLINE = "nav-underline"


class NavAlignment(enum.Enum):
    """Alignment for the nav element"""

    DEFAULT = ""
    FILL = "nav-fill"
    JUSTIFIED = "nav-justified"


class NavElement:
    """Base class for nav components"""

    @property
    def active(self) -> bool:
        """Whether the element is active"""
        return False

    @property
    def enabled(self) -> bool:
        """Whether the element is enabled"""
        return True

    def __tag__(self) -> dom_tag:
        warnings.warn(BootlaceWarning(f"Unhandled element {self.__class__.__name__}"), stacklevel=2)
        return tags.comment(f"unhandled element {self.__class__.__name__}")

    def element_state(self, tag: dom_tag) -> dom_tag:
        """Apply :attr:`active` and :attr:`enabled` states to the tag."""
        if not isinstance(tag, tags.html_tag):
            return tag

        if self.active:
            tag.classes.add("active")
            tag.attributes["aria-current"] = "page"

        if not self.enabled:
            tag.classes.add("disabled")
            tag["aria-disabled"] = "true"
        return tag


@attrs.define
class Link(NavElement):
    """A link in the nav bar, either for a view or a literal URL"""

    #: The link to display, either a URL or a view
    link: links.LinkBase

    #: The ID of the element
    id: str = attrs.field(factory=element_id.factory("nav-link"))

    @classmethod
    def with_url(cls, url: str, text: str | Image, **kwargs: Any) -> "Link":
        """Create a link with a URL."""
        return cls(link=links.Link(url=url, text=text, **kwargs))

    @classmethod
    def with_view(cls, endpoint: str, text: str | Image, **kwargs: Any) -> "Link":
        """Create a link with a view."""
        return cls(link=links.View(endpoint=endpoint, text=text, **kwargs))

    @property
    def active(self) -> bool:
        """Whether the link is active."""
        return self.link.active

    @property
    def enabled(self) -> bool:
        """Whether the link is enabled."""
        return self.link.enabled

    @property
    def url(self) -> str:
        """The URL for the link."""
        return self.link.url

    def __tag__(self) -> dom_tag:
        a = as_tag(self.link)
        if isinstance(a, tags.html_tag):
            a["id"] = self.id
            a.classes.add("nav-link")

        return self.element_state(a)


@attrs.define
class Separator(NavElement):
    """A separator in dropdown menus"""

    def __tag__(self) -> tags.html_tag:
        return tags.hr(cls="dropdown-divider")


@attrs.define
class Text(NavElement):
    """A text element in the nav bar"""

    text: str

    @property
    def enabled(self) -> bool:
        return False

    def __tag__(self) -> dom_tag:
        tag = tags.span(self.text, cls="nav-link")
        return self.element_state(tag)


@attrs.define
class SubGroup(NavElement):
    """Any grouping of items in the nav bar"""

    items: list[NavElement] = attrs.field(factory=list)

    @property
    def active(self) -> bool:
        return any(item.active for item in self.items)
