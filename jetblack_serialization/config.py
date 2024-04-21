"""Serializer Config"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Mapping, Optional, Type

from jetblack_iso8601 import (
    iso8601_to_datetime,
    iso8601_to_timedelta,
    datetime_to_iso8601,
    timedelta_to_iso8601,
)


def _same_name(name: str) -> str:
    return name


def to_datetime(text: str) -> datetime:
    value = iso8601_to_datetime(text)
    if value is None:
        raise ValueError('Unable to parse iso8601 timestamp')
    return value


def to_timedelta(text: str) -> timedelta:
    value = iso8601_to_timedelta(text)
    if value is None:
        raise ValueError('Unable to parse iso8601 timestamp')
    return value


ValueSerializer = Callable[[Any], Any]
ValueDeserializer = Callable[[str], Any]
ValueSerializers = Mapping[Type, ValueSerializer]
ValueDeserializers = Mapping[Type, ValueDeserializer]

VALUE_SERIALIZERS: ValueSerializers = {
    datetime: datetime_to_iso8601,
    timedelta: timedelta_to_iso8601,
    Decimal: float
}
VALUE_DESERIALIZERS: ValueDeserializers = {
    datetime: to_datetime,
    timedelta: to_timedelta,
    Decimal: Decimal
}


class SerializerConfig:
    """Configuration for serialization"""

    def __init__(
        self,
        serialize_key: Optional[Callable[[str], str]],
        deserialize_key: Optional[Callable[[str], str]],
        *,
        pretty_print: bool = False,
        value_serializers: ValueSerializers = VALUE_SERIALIZERS,
        value_deserializers: ValueDeserializers = VALUE_DESERIALIZERS
    ) -> None:
        self.serialize_key = serialize_key or _same_name
        self.deserialize_key = deserialize_key or _same_name
        self.pretty_print = pretty_print
        self.value_serializers = value_serializers
        self.value_deserializers = value_deserializers
