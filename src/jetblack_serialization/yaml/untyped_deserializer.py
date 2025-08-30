"""Untyped YAML deserialization"""

from typing import Any

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..json.untyped_deserializer import from_untyped_object

from .encoding import YAMLDecoder, DECODE_YAML


def deserialize_untyped(
        text: str | bytes | bytearray,
        config: SerializerConfig | None = None,
        decode: YAMLDecoder | None = None
) -> Any:
    json_value = (decode or DECODE_YAML)(text)
    return from_untyped_object(json_value, config or DEFAULT_CONFIG)
