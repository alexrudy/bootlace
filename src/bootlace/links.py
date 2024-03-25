import abc
from typing import Any

import attrs
from dominate import tags
from flask import url_for

from .util import as_tag
from .util import is_active_endpoint
from .util import MaybeTaggable

__all__ = ["Link", "View"]


@attrs.define(kw_only=True, frozen=True)
class LinkBase(abc.ABC):
    text: MaybeTaggable

    @abc.abstractproperty
    def active(self) -> bool:
        raise NotImplementedError("LinkBase.active must be implemented in a subclass")

    @abc.abstractproperty
    def enabled(self) -> bool:
        raise NotImplementedError("LinkBase.enabled must be implemented in a subclass")

    @abc.abstractproperty
    def url(self) -> str:
        raise NotImplementedError("LinkBase.url must be implemented in a subclass")

    def __tag__(self) -> tags.html_tag:

        return tags.a(as_tag(self.text), href=self.url)


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
    endpoint: str

    #: The keyword arguments to pass to :func:`~flask.url_for`
    url_kwargs: dict[str, Any] = attrs.field(factory=dict)

    #: Whether to ignore the query string when checking if the link is active
    ignore_query: bool = True

    #: Whether the link is enabled.
    enabled: bool = True

    @property
    def url(self) -> str:
        """The URL to link to, constructed using :func:`~flask.url_for`."""
        return url_for(self.endpoint, **self.url_kwargs)

    @property
    def active(self) -> bool:
        """Whether the link is active, based on the current request endpoint."""
        return is_active_endpoint(self.endpoint, self.url_kwargs, self.ignore_query)
