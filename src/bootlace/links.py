import abc

import attrs
from dominate import tags

from .endpoint import convert_endpoint
from .endpoint import Endpoint
from .util import as_tag
from .util import MaybeTaggable
from .util import Tag

__all__ = ["Link", "View"]


@attrs.define(kw_only=True, frozen=True)
class LinkBase(abc.ABC):
    text: MaybeTaggable

    a: Tag = Tag(tags.a)

    @property
    @abc.abstractmethod
    def active(self) -> bool:
        raise NotImplementedError("LinkBase.active must be implemented in a subclass")

    @property
    @abc.abstractmethod
    def enabled(self) -> bool:
        raise NotImplementedError("LinkBase.enabled must be implemented in a subclass")

    @property
    @abc.abstractmethod
    def url(self) -> str:
        raise NotImplementedError("LinkBase.url must be implemented in a subclass")

    def __tag__(self) -> tags.html_tag:
        return self.a(as_tag(self.text), href=self.url)


@attrs.define(kw_only=True, frozen=True)
class Link(LinkBase):
    """A raw link to a URL."""

    #: The URL to link to
    url: str

    #: Whether the link is active
    active: bool = False

    #: Whether the link is enabled
    enabled: bool = True


@attrs.define(kw_only=True, frozen=True)
class View(LinkBase):
    """Link to a Flask view."""

    #: The endpoint to link to, for use with Flask's :func:`~flask.url_for`
    endpoint: Endpoint = attrs.field(converter=convert_endpoint)

    #: Whether the link is enabled.
    enabled: bool = True

    @property
    def url(self) -> str:
        """The URL to link to, constructed using :func:`~flask.url_for`."""
        return self.endpoint.url

    @property
    def active(self) -> bool:
        """Whether the link is active, based on the current request endpoint."""
        return self.endpoint.active
