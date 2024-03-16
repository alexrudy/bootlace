from typing import ClassVar

import attrs
from dominate import svg
from dominate import tags
from flask import url_for


@attrs.define
class Icon:
    """A Bootstrap icon"""

    endpoint: ClassVar[str] = "core.static"
    filename: ClassVar[str] = "icons/bootstrap-icons.svg"

    name: str
    width: int = 16
    height: int = 16

    @property
    def url(self) -> str:
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
