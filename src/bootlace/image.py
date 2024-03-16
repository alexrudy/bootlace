import attrs
from dominate import tags


@attrs.define(kw_only=True, frozen=True)
class Image:
    alt: str
    src: str
    width: int
    height: int

    def __tag__(self) -> tags.html_tag:
        return tags.img(src=self.src, alt=self.alt, width=self.width, height=self.height)
