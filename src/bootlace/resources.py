from collections.abc import Iterator
from pathlib import PosixPath as Path

import attrs
from dominate import tags
from dominate.dom_tag import dom_tag
from dominate.util import container

from bootlace.endpoint import Endpoint


@attrs.define
class Resources:
    """Bootstrap resource extension for bootlace"""

    endpoint: Endpoint

    resources: list[str] = attrs.field(factory=list)

    def iter_resources(self, extension: str | None = None) -> Iterator[str]:
        if extension and not extension.startswith("."):
            extension = f".{extension}"

        for resource in self.resources:
            if extension and Path(resource).suffix == extension:
                yield resource

    def css(self) -> dom_tag:
        collection = container()

        for filename in self.iter_resources(".css"):
            url = self.endpoint(filename=filename)
            collection.add(tags.link(rel="stylesheet", href=url))

        return collection

    def js(self) -> dom_tag:
        collection = container()

        for filename in self.iter_resources(".js"):
            url = self.endpoint(filename=filename)
            collection.add(tags.script(src=url))

        return collection
