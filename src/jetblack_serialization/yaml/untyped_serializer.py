"""Untyped YAML serialization"""

from typing import Any

from ..config import SerializerConfig
from ..json.untyped_serializer import from_untyped_object

from .encoding import YAMLEncoder, ENCODE_YAML


def serialize_untyped(
        obj: Any,
        config: SerializerConfig,
        encode: YAMLEncoder | None = None
) -> str:
    if encode is None:
        encode = ENCODE_YAML

    json_obj = from_untyped_object(obj, config)
    return encode(json_obj)
