import json
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Any as AnyType
from typing import (
    Dict,
    List,
    Sequence,
    Type,
    get_args,
    get_origin,
    get_type_hints,
)

from communal.casing import to_camel_case
from communal.collections import is_mapping
from communal.enum import StringEnum
from communal.iterables import is_sequence
from communal.nesting import nested_get, nested_set
from communal.nulls import Omitted
from pydantic import BaseModel, ConfigDict, create_model
from pydantic.fields import FieldInfo

from sartorial.types import JSON_SCHEMA_DEFAULT_TYPES, JSONSchemaFormatted


def json_schema_extra(schema: Dict[str, AnyType], model: Type["Schema"]) -> None:
    model.json_schema_extra(schema, model)


warnings.filterwarnings(
    "ignore",
    message=r'Field name ".*" shadows an attribute in parent ".*"',
    category=UserWarning,
    module="pydantic._internal._fields",
)


class AnnotatedFieldInfo(FieldInfo):
    __slots__ = FieldInfo.__slots__ + ("key",)

    def __init__(self, *args, key: str, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key


@dataclass
class SchemaRefQueueItem:
    key_path: List[str]
    model_name: str
    is_ref: bool
    path_default: AnyType
    is_array: bool
    required_props: List[str]
    props: Dict[str, AnyType]


class Schema(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        json_schema_extra=json_schema_extra,
        arbitrary_types_allowed=True,
    )

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        model_fields = cls.model_fields
        for name, field in model_fields.items():
            setattr(cls, name, AnnotatedFieldInfo(**field._attributes_set, key=name))

    @classmethod
    def json_schema_extra(
        cls, schema: Dict[str, AnyType], model: Type["Schema"]
    ) -> None:
        schema.setdefault("properties", {})
        type_hints = get_type_hints(model)

        for name in cls.model_fields:
            field_type = type_hints.get(name)
            outer_field_type = field_type
            if field_type:
                origin = get_origin(field_type)
                if origin:
                    args = get_args(field_type)
                    outer_field_type = origin
                    if args:
                        field_type = args[0]
            if not isinstance(field_type, type):
                field_type = type(field_type)

            is_array = False
            if outer_field_type and not isinstance(outer_field_type, type):
                outer_field_type = type(outer_field_type)

            if outer_field_type and outer_field_type is not field_type:
                origin = outer_field_type
                if issubclass(origin, Sequence):
                    is_array = True

            is_enum = issubclass(field_type, Enum)

            if field_type in JSONSchemaFormatted.__type_format_strings__:
                (
                    schema_type,
                    schema_format,
                ) = JSONSchemaFormatted.__type_format_strings__[field_type]

                props = {
                    "type": schema_type,
                    "format": schema_format,
                }

                if is_enum:
                    props["enum"] = [
                        {"name": k, "value": v.value}
                        for k, v in field_type.__members__.items()
                    ]

                    types = {type(e.value) for e in field_type.__members__.values()}
                    if types == {str}:
                        props["type"] = "string"
                    elif types == {int}:
                        props["type"] = "integer"
                    elif types == {float}:
                        props["type"] = "number"
                    elif types == {bool}:
                        props["type"] = "boolean"
                    elif types == {list}:
                        props["type"] = "array"
                    elif types == {type(None)}:
                        props["type"] = "null"

                    props["title"] = field_type.__name__

                if is_array:
                    schema["properties"][name] = {"type": "array", "items": props}
                else:
                    schema["properties"][name] = props

    @classmethod
    def from_schema_dict(cls, schema: Dict, name: str = Omitted):
        if name is Omitted:
            name = schema["title"]

        required_props = schema.get("required", [])
        original_props = schema.get("properties", {})

        all_fields = {}
        queue = [
            SchemaRefQueueItem(
                key_path=[],
                model_name=name,
                is_ref=False,
                path_default=None,
                is_array=False,
                required_props=required_props,
                props=original_props,
            )
        ]

        rel_key_paths = []

        ref_cache = {}

        while queue:
            item = queue.pop()
            key_path = item.key_path
            model_name = item.model_name
            is_ref = item.is_ref
            path_default = item.path_default
            is_array = item.is_array
            required_props = item.required_props
            props = item.props

            fields = {}
            required = set(required_props)

            for key, prop in props.items():
                is_required = key in required
                default_value = ... if is_required else None
                if "default" in prop:
                    default_value = prop["default"]

                ref_is_array = False
                ref_name = None
                if "$ref" in prop.get("items", prop):
                    ref_prop = prop.get("items", prop)["$ref"]
                    ref_is_array = "items" in prop
                    ref_path = [p for p in ref_prop.split("/") if p != "#"]
                    if ref_path:
                        ref_name = ref_path[-1]
                    ref = nested_get(schema, ref_path)
                    if "properties" in ref:
                        ref_props = ref["properties"]
                        ref_required_props = ref.get("required", [])
                        queue.append(
                            SchemaRefQueueItem(
                                key_path=key_path + [key],
                                model_name=ref_name,
                                is_ref=True,
                                path_default=default_value,
                                is_array=ref_is_array,
                                required_props=ref_required_props,
                                props=ref_props,
                            )
                        )
                        continue
                    else:
                        prop = ref
                field_type = prop.get("type")
                format_type = prop.get("format")
                enum_values = prop.get("enum")

                field_is_array = field_is_object = False
                use_dict_typed_value = False
                if field_type == "array":
                    items = prop.get("items", {})
                    field_type = items.get("type", field_type)
                    format_type = items.get("format")
                    enum_values = items.get("enum")
                    field_is_array = True
                elif field_type == "object":
                    additional_props = prop.get("additionalProperties")
                    if not additional_props:
                        additional_props = {}
                    field_object_value_type = additional_props.get("type")
                    if field_object_value_type:
                        field_type = field_object_value_type
                        use_dict_typed_value = True
                    format_type = additional_props.get("format")
                    enum_values = additional_props.get("enum")
                    field_is_object = True

                value_type = None
                if format_type:
                    value_type = JSONSchemaFormatted.get_type(
                        schema_type=field_type, schema_format=format_type
                    )
                if not value_type:
                    value_type = JSON_SCHEMA_DEFAULT_TYPES.get(field_type, value_type)

                if value_type and not enum_values:
                    if field_is_array:
                        value_type = List[value_type]
                    elif field_is_object:
                        if use_dict_typed_value:
                            value_type = Dict[str, value_type]
                        else:
                            value_type = Dict
                elif enum_values:
                    title = (
                        prop.get("title", to_camel_case(key))
                        if not field_is_array
                        else prop["items"].get("title", to_camel_case(key))
                    )
                    if is_ref and ref_name:
                        title = ref_name

                    if title in ref_cache:
                        value_type = ref_cache[title]
                    else:
                        if is_mapping(enum_values):
                            value_type = StringEnum(title, enum_values)
                        elif is_sequence(enum_values) and is_mapping(enum_values[0]):
                            value_type = StringEnum(
                                title,
                                [(item["name"], item["value"]) for item in enum_values],
                            )
                        else:
                            value_type = Enum(
                                title, {item: item for item in enum_values}
                            )

                        if is_ref:
                            ref_cache[title] = value_type

                    if field_is_array or ref_is_array:
                        value_type = List[value_type]
                if value_type:
                    fields[key] = (value_type, default_value)

            if not key_path:
                all_fields.update(fields)
            else:
                rel_key_paths.append(
                    (key_path, model_name, path_default, is_array, fields)
                )

        base = getattr(cls, "__base__", cls)
        for key_path, model_name, path_default, is_array, fields in reversed(
            rel_key_paths
        ):
            if model_name in ref_cache:
                model = ref_cache[model_name]
            else:
                rel_fields = nested_get(all_fields, key_path, {})
                model = create_model(
                    model_name, **dict(rel_fields, **fields), __base__=base
                )
                ref_cache[model_name] = model
            if is_array:
                model = List[model]
            nested_set(all_fields, key_path, (model, path_default))

        return create_model(name, **all_fields, __base__=cls)

    @classmethod
    def from_schema_json(cls, schema_json: str, name: str = Omitted):
        schema = json.loads(schema_json)
        return cls.from_schema_dict(schema, name=name)

    @classmethod
    def to_schema_dict(cls):
        return cls.model_json_schema()

    @classmethod
    def to_schema_json(cls):
        return json.dumps(cls.model_json_schema())

    @classmethod
    def from_dict(cls, d: dict):
        return cls(**d)

    @classmethod
    def from_json(cls, data_json: str):
        data = json.loads(data_json)
        return cls.from_dict(data)

    def to_dict(self):
        return self.model_dump()

    def to_json(self):
        return self.model_dump_json()

    @classmethod
    def create_model(cls, model, fields, base=None):
        if hasattr(model, "__name__"):
            name = model.__name__
        elif isinstance(model, str):
            name = model
        else:
            raise ValueError("Arg model must be class or string")

        if not base:
            base = cls
        return create_model(name, __base__=base, **fields)


class ModelSchema(Schema):
    model_config = ConfigDict(
        Schema.model_config, from_attributes=True, arbitrary_types_allowed=True
    )

    @classmethod
    def from_model(cls, model):
        model_name = model.__name__

        def json_schema_extra(
            json_schema: Dict[str, AnyType], schema_cls: Type["ModelSchema"]
        ) -> None:
            schema_cls.json_schema_extra(json_schema, schema_cls)

            if hasattr(model, "add_to_json_schema"):
                model.add_to_json_schema(json_schema)

        name = f"{model_name}{cls.__name__}"
        qualified_name = f"{cls.__module__}.{name}"
        model_cls = type(
            name,
            (cls,),
            {
                "__base__": cls,
                "__model__": model,
                "__module__": cls.__module__,
                "__qualname__": qualified_name,
                "model_config": ConfigDict(
                    cls.model_config, json_schema_extra=json_schema_extra
                ),
            },
        )
        return model_cls


class StrictSchema(Schema):
    model_config = ConfigDict(Schema.model_config, extra="forbid")


class StrictModelSchema(ModelSchema):
    model_config = ConfigDict(ModelSchema.model_config, extra="forbid")
