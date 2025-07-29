"""Typed YAML deserialization"""

from typing import Any

from ..config import SerializerConfig
from ..json import from_json_value
from ..types import Annotation

from .encoding import YAMLDecoder, DECODE_YAML


def deserialize_typed(
        text: str | bytes | bytearray,
        annotation: Annotation,
        config: SerializerConfig,
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
    if decode is None:
        decode = DECODE_YAML
    json_value = decode(text)
    return from_json_value(config, json_value, annotation)
