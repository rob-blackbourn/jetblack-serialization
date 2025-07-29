"""Untyped YAML serialization"""

from typing import Any

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..json.untyped_serializer import from_untyped_object

from .encoding import YAMLEncoder, ENCODE_YAML


def serialize_untyped(
        obj: Any,
        config: SerializerConfig | None = None,
        encode: YAMLEncoder | None = None
) -> str:
    json_obj = from_untyped_object(obj, config or DEFAULT_CONFIG)
    return (encode or ENCODE_YAML)(json_obj)
