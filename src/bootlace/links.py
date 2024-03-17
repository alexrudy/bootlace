import abc
from typing import Any

import attrs
from dominate import tags
from flask import request
from flask import url_for

from .util import as_tag
from .util import MaybeTaggable


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
    url: str
    active: bool = False
    enabled: bool = True


@attrs.define(kw_only=True, frozen=True)
class View(LinkBase):
    endpoint: str
    url_kwargs: dict[str, Any] = attrs.field(factory=dict)
    ignore_query: bool = True
    enabled: bool = True

    @property
    def url(self) -> str:
        return url_for(self.endpoint, **self.url_kwargs)

    @property
    def active(self) -> bool:
        if request.endpoint != self.endpoint:
            return False

        if request.url_rule is None:  # pragma: no cover
            return False

        rule_url = request.url_rule.build(self.url_kwargs, append_unknown=not self.ignore_query)

        if rule_url is None:  # pragma: no cover
            return False

        _, url = rule_url

        return url == request.path
