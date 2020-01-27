"""Serializer Config"""

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Type

from .iso_8601 import (
    iso_8601_to_datetime,
    iso_8601_to_timedelta,
    datetime_to_iso_8601,
    timedelta_to_iso_8601,
)


def _same_name(name: str) -> str:
    return name


VALUE_DESERIALIZERS: Dict[Type, Callable[[str], Any]] = {
    datetime: iso_8601_to_datetime,
    timedelta: iso_8601_to_timedelta
}
VALUE_SERIALIZERS: Dict[Type, Callable[[Any], str]] = {
    datetime: datetime_to_iso_8601,
    timedelta: timedelta_to_iso_8601
}


class SerializerConfig:
    """Configuration for serialization"""

    def __init__(
        self,
        serialize_key: Optional[Callable[[str], str]],
        deserialize_key: Optional[Callable[[str], str]],
        *,
        pretty_print: bool = False,
        value_serializers=VALUE_SERIALIZERS,
        value_deserializers=VALUE_DESERIALIZERS
    ) -> None:
        self.serialize_key = serialize_key or _same_name
        self.deserialize_key = deserialize_key or _same_name
        self.pretty_print = pretty_print
        self.value_serializers = value_serializers
        self.value_deserializers = value_deserializers
