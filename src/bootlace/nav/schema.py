from collections.abc import Mapping
from typing import TYPE_CHECKING
from typing import Any

import attrs
from domilite import tags
from markupsafe import Markup
from marshmallow import Schema
from marshmallow import ValidationError
from marshmallow import fields
from marshmallow import post_load
from marshmallow_oneofschema.one_of_schema import OneOfSchema

from bootlace import links
from bootlace.endpoint import Endpoint
from bootlace.util import MaybeTaggable
from bootlace.util import Tag
from bootlace.util import render

if TYPE_CHECKING:
    from bootlace.nav.core import NavElement


class NavSchema(OneOfSchema):
    """Registry for nav element schemas"""

    type_field = "__type__"
    type_schemas: dict[str, type[Schema]] = {}  # pyright: ignore

    def __init__(self, **kwargs: Any) -> None:
        self.register_all()
        super().__init__(**kwargs)

    @classmethod
    def register_all(cls) -> None:
        """Register a schema for a nav element"""
        from bootlace.nav.core import NavElement

        for element in NavElement._NAV_ELEMENT_REGISTRY.values():
            cls.register(element)

    @classmethod
    def register(cls, element: "type[NavElement]") -> None:
        """Register a schema for a nav element"""
        if element.__name__ not in cls.type_schemas:
            schema = build_schema(element)
            cls.type_schemas[element.__name__] = schema


class BaseSchema(Schema):
    """Base schema with reloading"""

    @post_load
    def make_instance(self, data: dict[str, Any], **kwargs: Any) -> Any:
        return self.Meta.element(**data)  # type: ignore


class DomTagField(fields.Field):
    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: Any) -> Any:
        if value is None:  # pragma: no cover
            return None

        if not (isinstance(value, tags.html_tag) or issubclass(value, tags.html_tag)):  # pragma: no cover
            raise ValidationError(f"Unknown tag type: {type(value)!r}: {value!r}")

        return value.name

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> Any:
        if value is None:  # pragma: no cover
            return None
        return tags.html_tag.find_tag_type(value)


class Set(fields.List):
    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: Any) -> Any:
        if value is None:  # pragma: no cover
            return None
        return list(value)

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> Any:
        if value is None:  # pragma: no cover
            return None
        return set(value)


class TagSchema(Schema):
    tag = DomTagField()
    classes = Set(fields.String())
    attributes = fields.Dict()

    class Meta:
        element = Tag

    @post_load
    def make_instance(self, data: dict[str, Any], **kwargs: Any) -> Any:
        return Tag(**data)


class TaggableField(fields.Field):
    def _serialize(self, value: Any, attr: str | None, obj: Any, **kwargs: Any) -> Any:
        if value is None:  # pragma: no cover
            return None
        return str(render(value))

    def _deserialize(
        self,
        value: Any,
        attr: str | None,
        data: Mapping[str, Any] | None,
        **kwargs: Any,
    ) -> Any:
        if value is None:  # pragma: no cover
            return None
        return Markup(value)


ATTRS_FIELD_TYPE_MAP = {
    str: fields.String,
    str | None: lambda: fields.String(allow_none=True),
    int: fields.Integer,
    float: fields.Float,
    bool: fields.Boolean,
    Tag: lambda: fields.Nested(TagSchema),
    links.LinkBase: lambda: fields.Nested(LinkBaseSchema),
    MaybeTaggable: TaggableField,
}


def build_schema(element: "type[NavElement]") -> type[Schema]:
    form_fields: dict[str, fields.Field] = {}
    for field in attrs.fields(element):  # type: ignore
        ff = field.metadata.get("form", None)
        if ff is None:
            if field.type not in ATTRS_FIELD_TYPE_MAP:  # pragma: no cover
                raise ValueError(f"Unknown field type {field.type!r}")

            form_fields[field.name] = ATTRS_FIELD_TYPE_MAP[field.type]()  # type: ignore
        else:
            form_fields[field.name] = ff

    meta = type("Meta", (), {"element": element})

    attributes: dict[str, Any] = {"Meta": meta, **form_fields}

    return type(f"{element.__name__}Schema", (BaseSchema,), attributes)


class EndpointSchema(BaseSchema):
    name = fields.String(required=True)
    url_kwargs = fields.Dict()
    ignore_query = fields.Boolean(required=True)

    class Meta:
        element = Endpoint


class LinkSchema(BaseSchema):
    text = TaggableField()
    a = fields.Nested(TagSchema)
    url = fields.String(required=True)
    active = fields.Boolean(required=True)
    enabled = fields.Boolean(required=True)

    class Meta:
        element = links.Link


class ViewLinkSchema(BaseSchema):
    text = TaggableField()
    a = fields.Nested(TagSchema)
    endpoint = fields.Nested(EndpointSchema)
    enabled = fields.Boolean()

    class Meta:
        element = links.View


class LinkBaseSchema(OneOfSchema):
    type_field = "__type__"
    type_schemas: dict[str, type[Schema]] = {"Link": LinkSchema, "View": ViewLinkSchema}  # pyright: ignore
