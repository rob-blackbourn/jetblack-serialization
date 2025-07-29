"""Untyped YAML deserialization"""

from typing import Any

from ..config import SerializerConfig
from ..json.untyped_deserializer import from_untyped_object

from .encoding import YAMLDecoder, DECODE_YAML


def deserialize_untyped(
        text: str | bytes | bytearray,
        config: SerializerConfig,
        decode: YAMLDecoder | None = None
) -> Any:
    if decode is None:
        decode = DECODE_YAML

    json_value = decode(text)
    return from_untyped_object(json_value, config)
