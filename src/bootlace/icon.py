from typing import ClassVar

import attrs
from dominate import svg as svg_tag
from dominate.dom_tag import dom_tag

from bootlace.endpoint import Endpoint
from bootlace.util import Tag


__all__ = ["Icon"]


@attrs.define
class Icon:
    """A Bootstrap icon

    This class supports the :func:`as_tag` protocol to display itself.
    """

    #: Endpoint name for getting the Bootstrap Icon SVG file
    endpoint: ClassVar[Endpoint] = Endpoint.from_name("bootlace.static", filename="icons/bootstrap-icons.svg")

    #: Name of the icon
    name: str

    svg: Tag = Tag(
        svg_tag.svg,
        attributes={"role": "img", "fill": "currentColor", "width": "16", "height": "16"},
        classes={"bi", "me-1", "pe-none", "align-self-center"},
    )

    use: Tag = Tag(svg_tag.use)

    @property
    def url(self) -> str:
        """The URL for the SVG source for the icon"""
        return self.endpoint(_anchor=self.name)

    def __tag__(self) -> dom_tag:
        return self.svg(
            self.use(xlink_href=self.url),
        )
