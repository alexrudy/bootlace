from collections.abc import Iterator
from collections.abc import Mapping
from typing import Any

import attrs
from flask import Blueprint
from flask import url_for

from bootlace.util import is_active_endpoint


@attrs.define(frozen=True, init=False)
class KeywordArguments(Mapping[str, Any]):
    """
    A mapping of keyword arguments for a URL endpoint,
    which is frozen and hashable for use as a key in a dictionary.
    """

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


@attrs.define(frozen=True, repr=False, kw_only=True)
class Endpoint:
    """An endpoint for a breadcrumb, as captured at registration"""

    #: The flask context, if any
    context: None | Blueprint = None

    #: The endpoint name
    name: str

    #: The keyword arguments for the endpoint used with url_for
    url_kwargs: KeywordArguments = attrs.field(factory=lambda: KeywordArguments(), converter=KeywordArguments)

    #: Whether to ignore the query string when checking for active status
    ignore_query: bool = True

    @classmethod
    def from_name(cls, name: str, **kwargs: Any) -> "Endpoint":
        """Create an endpoint from a name and keyword arguments"""
        ignore_query = kwargs.pop("ignore_query", True)

        return cls(name=name, url_kwargs=KeywordArguments(**kwargs), ignore_query=ignore_query)

    @property
    def url(self) -> str:
        """The URL for the endpoint"""
        return self.build()

    def build(self, **kwds: Any) -> str:
        """Build the URL for the endpoint with additional keyword arguments"""
        if isinstance(self.context, Blueprint):
            name = f"{self.context.name}.{self.name}"
            return url_for(name, **self.url_kwargs, **kwds)

        return url_for(self.name, **self.url_kwargs, **kwds)

    @property
    def active(self) -> bool:
        """Whether the endpoint is active"""
        return is_active_endpoint(self.name, self.url_kwargs, self.ignore_query)

    def __call__(self, **kwds: Any) -> str:
        return self.build(**kwds)

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


def convert_endpoint(endpoint: str | Endpoint) -> Endpoint:
    """Convert a string endpoint to an Endpoint object"""
    if isinstance(endpoint, str):
        return Endpoint.from_name(endpoint)

    return endpoint
