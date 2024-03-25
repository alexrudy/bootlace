from typing import ClassVar

import attrs
from dominate import svg
from dominate import tags
from flask import url_for


__all__ = ["Icon"]


@attrs.define
class Icon:
    """A Bootstrap icon

    This class supports the :func:`as_tag` protocol to display itself.
    """

    #: Endpoint name for getting the Bootstrap Icon SVG file
    endpoint: ClassVar[str] = "static"

    #: Filename for the Bootstrap Icon SVG file
    filename: ClassVar[str] = "icons/bootstrap-icons.svg"

    #: Name of the icon
    name: str

    #: Width of the icon
    width: int = 16

    #: Height of the icon
    height: int = 16

    @property
    def url(self) -> str:
        """The URL for the SVG source for the icon"""
        return url_for(self.endpoint, filename=self.filename, _anchor=self.name)

    def __tag__(self) -> tags.html_tag:
        classes = ["bi", "me-1", "pe-none", "align-self-center"]
        return svg.svg(
            svg.use(xlink_href=self.url),
            cls=" ".join(classes),
            role="img",
            width=self.width,
            height=self.height,
            fill="currentColor",
        )
