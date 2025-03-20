from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from pathlib import Path
from typing import Any as AnyType
from typing import ClassVar, Type
from uuid import UUID

from communal.nulls import DoesNotExist, Omitted
from pydantic import GetCoreSchemaHandler
from pydantic.json_schema import GetJsonSchemaHandler, JsonSchemaValue
from pydantic_core import CoreSchema, SchemaSerializer, core_schema

JSON_SCHEMA_DEFAULT_TYPES = {
    "string": str,
    "number": float,
    "integer": int,
    "boolean": bool,
    "object": dict,
    "array": list,
    "null": type(None),
}


class JSONSchemaFormatted:
    __type_format_strings__ = {
        Decimal: ("number", "decimal"),
        datetime: ("string", "date-time"),
        date: ("string", "date"),
        time: ("string", "time"),
        timedelta: ("string", "duration"),
        Enum: ("string", "enum"),
        UUID: ("string", "uuid"),
        IPv4Address: ("string", "ipv4"),
        IPv4Interface: ("string", "ipv4-interface"),
        IPv4Network: ("string", "ipv4-network"),
        IPv6Address: ("string", "ipv6"),
        IPv6Interface: ("string", "ipv6-interface"),
        IPv6Network: ("string", "ipv6-network"),
        Path: ("string", "path"),
    }
    __string_type_formats__ = {}
    for k, (t, f) in __type_format_strings__.items():
        __string_type_formats__.setdefault(t, {})
        __string_type_formats__[t][f] = k

    __python_type__: ClassVar[Type] = Omitted
    __schema_type__: ClassVar[str] = "string"
    __schema_format__: ClassVar[str] = Omitted

    @classmethod
    def register(cls, python_type: Type, schema_type: str, schema_format: str):
        if (
            schema_type in cls.__string_type_formats__
            and schema_format in cls.__string_type_formats__[schema_type]
        ):
            raise ValueError(
                f"schema_format {schema_format} for type {schema_type} is already registered to {cls.__string_type_formats__[schema_type][schema_format]}"
            )
        cls.__string_type_formats__.setdefault(schema_type, {})
        cls.__string_type_formats__[schema_type][schema_format] = python_type
        if python_type not in cls.__type_format_strings__:
            cls.__type_format_strings__[python_type] = (schema_type, schema_format)

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "__python_type__" not in cls.__dict__:
            cls.__python_type__ = cls
        if not cls.__schema_format__:
            raise ValueError("__schema_format__ is required")
        if "__schema_format__" not in cls.__dict__ and (
            not hasattr(cls, ".__pydantic_generic_metadata__")
            or not cls.__pydantic_generic_metadata__.get("origin")
        ):
            raise ValueError("__schema_format__ is required for generic base classes")
        cls.register(cls.__python_type__, cls.__schema_type__, cls.__schema_format__)

    @classmethod
    def get_type(
        cls, schema_type: str, schema_format: str, default: AnyType = DoesNotExist
    ) -> Type:
        return cls.__string_type_formats__.get(schema_type, {}).get(
            schema_format, default
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: core_schema.JsonSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)
        cls.add_to_field_json_schema(json_schema)
        return json_schema

    @classmethod
    def add_to_field_json_schema(cls, json_schema: JsonSchemaValue):
        json_schema.update(type=cls.__schema_type__, format=cls.__schema_format__)

    @classmethod
    def validate(cls, value: AnyType) -> AnyType:
        return cls.__python_type__(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: AnyType, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        options = {}
        if hasattr(source_type, "to_string"):
            options.update(
                serialization=core_schema.plain_serializer_function_ser_schema(
                    source_type.to_string,
                    info_arg=False,
                    return_schema=core_schema.str_schema(),
                )
            )

        schema = core_schema.no_info_after_validator_function(
            cls.validate, core_schema.any_schema(), **options
        )
        # Workaround from https://github.com/pydantic/pydantic/issues/7779
        if options:
            cls.__pydantic_serializer__ = SchemaSerializer(schema)
        return schema
