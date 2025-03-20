import datetime
from decimal import Decimal
from enum import Enum, EnumMeta
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from operator import attrgetter
from pathlib import Path
from types import GeneratorType
from typing import Any, Callable, Dict, Type, Union
from uuid import UUID

from dateutil.parser import parse as date_parse


def isoformat(o):
    return o.isoformat()


def enum_value(o):
    return o.value


def timedelta_total_seconds(td):
    return td.total_seconds()


def display_bool(b):
    return "Yes" if b else "No"


ENCODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    datetime.date: isoformat,
    datetime.datetime: isoformat,
    datetime.time: isoformat,
    datetime.timedelta: timedelta_total_seconds,
    Decimal: str,
    Enum: attrgetter("value"),
    EnumMeta: attrgetter("value"),
    frozenset: list,
    GeneratorType: list,
    IPv4Address: str,
    IPv4Interface: str,
    IPv4Network: str,
    IPv6Address: str,
    IPv6Interface: str,
    IPv6Network: str,
    Path: str,
    set: list,
    UUID: str,
}

DISPLAY_ENCODERS_BY_TYPE = ENCODERS_BY_TYPE.copy()
DISPLAY_ENCODERS_BY_TYPE.update(
    {
        Enum: attrgetter("name"),
        EnumMeta: attrgetter("name"),
        bool: display_bool,
    }
)


def any_to_datetime(d):
    if isinstance(d, datetime.datetime):
        return d
    elif isinstance(d, datetime.date):
        return datetime.datetime(*d.timetuple()[:6])
    else:
        return date_parse(d)


def any_to_datetime_iso_format(d):
    return any_to_datetime(d).isoformat()


def any_to_date(d):
    if isinstance(d, datetime.datetime):
        return d.date()
    elif isinstance(d, datetime.date):
        return d
    else:
        return date_parse(d).date()


def any_to_date_iso_format(d):
    return any_to_date(d).isoformat()


def any_to_time(t):
    if isinstance(t, datetime.datetime):
        return t.time()
    elif isinstance(t, datetime.date):
        return datetime.time(0)
    elif isinstance(t, datetime.time):
        return t
    else:
        return date_parse(t).time()


def any_to_decimal(d):
    if isinstance(d, Decimal):
        return d
    elif isinstance(d, str):
        return Decimal(d)
    else:
        return Decimal(str(d))


def any_to_uuid(u):
    if isinstance(u, UUID):
        return u
    else:
        return UUID(u)


def timedelta_parse(td):
    if isinstance(td, datetime.timedelta):
        return td
    else:
        return datetime.timedelta(seconds=td)


DECODERS_BY_TYPE: Dict[Type[Any], Callable[[Any], Any]] = {
    datetime.date: any_to_date,
    datetime.datetime: any_to_datetime,
    datetime.time: any_to_time,
    datetime.timedelta: timedelta_parse,
    Decimal: any_to_decimal,
    IPv4Address: IPv4Address,
    IPv4Interface: IPv4Interface,
    IPv4Network: IPv4Network,
    IPv6Address: IPv6Address,
    IPv6Interface: IPv6Interface,
    IPv6Network: IPv6Network,
    UUID: any_to_uuid,
}


def get_json_encoder(obj) -> Union[Callable[[Any], Any], None]:
    obj_type = type(obj)
    obj_type = getattr(obj_type, "__class__", obj_type)
    if obj_type not in ENCODERS_BY_TYPE:
        obj_type = getattr(obj, "__class__", obj_type)
    return ENCODERS_BY_TYPE.get(obj_type)


def encode_object(obj):
    encoder = get_json_encoder(obj)
    if encoder is None:
        return obj
    return encoder(obj)


def get_display_encoder(obj) -> Union[Callable[[Any], Any], None]:
    obj_type = type(obj)
    obj_type = getattr(obj_type, "__class__", obj_type)
    if obj_type not in DISPLAY_ENCODERS_BY_TYPE:
        obj_type = getattr(obj, "__class__", obj_type)
    return DISPLAY_ENCODERS_BY_TYPE.get(obj_type)


def get_display_value(obj):
    encoder = get_display_encoder(obj)
    if encoder is None:
        return obj
    return encoder(obj)


def is_builtin_json_encodable(obj):
    obj_type = type(obj)
    return obj_type in (str, bool, type(None), int, float, list, tuple, dict)


def is_json_encodable(obj):
    return is_builtin_json_encodable(obj) or get_json_encoder(obj) is not None


def decode_object(expected_type, obj):
    decoder = DECODERS_BY_TYPE.get(expected_type)
    if not decoder:
        try:
            return expected_type(obj)
        except (TypeError, ValueError):
            return obj
    return decoder(obj)


class Serializable:
    to_string: Callable[[Any], Any] = str
    from_string: Callable[[Any], Any]

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "from_string"):
            if not hasattr(cls, "__init__") or cls.__init__ == object.__init__:
                raise ValueError(
                    f"Serializable subclass {cls} must implement either __init__ or from_string"
                )
            cls.from_string = cls
        ENCODERS_BY_TYPE[cls] = cls.to_string
        DECODERS_BY_TYPE[cls] = cls.from_string
