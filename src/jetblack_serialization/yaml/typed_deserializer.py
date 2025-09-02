"""Typed YAML deserialization"""

from typing import Any

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..json import from_json_value
from ..types import Annotation

from .encoding import YAMLDecoder, DECODE_YAML


def deserialize_typed(
        text: str | bytes | bytearray,
        annotation: Annotation,
        config: SerializerConfig | None = None,
        decode: YAMLDecoder | None = None
) -> Any:
    """Convert YAML to an object.

    Args:
        text (str | bytes | bytearray): The YAML string
        annotation (str): The type annotation.
        config (SerializationConfig): The serializer config.

    Returns:
        Any: The deserialized object.
    """
    json_value = (decode or DECODE_YAML)(text)
    return from_json_value(json_value, annotation, config or DEFAULT_CONFIG)
