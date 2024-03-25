import attrs
from dominate import tags

__all__ = ["Image"]


@attrs.define(kw_only=True, frozen=True)
class Image:
    """An image tag"""

    #: Alt text for the image
    alt: str

    #: The URL for the image
    src: str

    #: The width of the image, in px
    width: int

    #: The height of the image, in px
    height: int

    def __tag__(self) -> tags.html_tag:
        return tags.img(src=self.src, alt=self.alt, width=self.width, height=self.height)
