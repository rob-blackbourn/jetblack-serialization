"""Serializer Config"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Sequence

from jetblack_iso8601 import (
    iso8601_to_datetime,
    iso8601_to_timedelta,
    datetime_to_iso8601,
    timedelta_to_iso8601,
)


def _same_name(name: str) -> str:
    return name


def _to_datetime(text: str) -> datetime:
    value = iso8601_to_datetime(text)
    if value is None:
        raise ValueError('Unable to parse iso8601 timestamp')
    return value


def _to_timedelta(text: str) -> timedelta:
    value = iso8601_to_timedelta(text)
    if value is None:
        raise ValueError('Unable to parse iso8601 timestamp')
    return value


type ValueSerializer = Callable[[Any], Any]
type ValueDeserializer = Callable[[str], Any]
type ValueSerializers = Sequence[tuple[type, ValueSerializer]]
type ValueDeserializers = Sequence[tuple[type, ValueDeserializer]]

VALUE_SERIALIZERS: ValueSerializers = (
    (datetime, datetime_to_iso8601),
    (timedelta, timedelta_to_iso8601),
    (Decimal, float)
)
VALUE_DESERIALIZERS: ValueDeserializers = (
    (datetime, _to_datetime),
    (timedelta, _to_timedelta),
    (Decimal, Decimal)
)


class SerializerConfig:
    """Configuration for serialization"""

    def __init__(
        self,
        key_serializer: Callable[[str], str] | None = None,
        key_deserializer: Callable[[str], str] | None = None,
        value_serializers: ValueSerializers | None = None,
        value_deserializers: ValueDeserializers | None = None,
    ) -> None:
        self.serialize_key = key_serializer or _same_name
        self.deserialize_key = key_deserializer or _same_name
        self.value_serializers = dict(
            value_serializers or VALUE_SERIALIZERS
        )
        self.value_deserializers = dict(
            value_deserializers or VALUE_DESERIALIZERS
        )


DEFAULT_CONFIG = SerializerConfig()
