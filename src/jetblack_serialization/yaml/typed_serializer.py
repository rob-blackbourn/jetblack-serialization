"""Typed YAML serialization"""

from typing import Any

from ..config import SerializerConfig
from ..json import JSONValue
from ..json.annotations import is_json_annotation, get_json_annotation
from ..json.typed_serializer import from_json_value
from ..types import Annotation

from .encoding import YAMLEncoder, ENCODE_YAML


def serialize_typed(
        obj: Any,
        annotation: Annotation,
        config: SerializerConfig,
        encode: YAMLEncoder | None = None
) -> str:
    """Serialize an object to YAML.

    Args:
        obj (Any): The object to serialize.
        annotation (Annotation): The objects type annotation.
        config (YAMLSerializerConfig): The serialization config.

    Raises:
        TypeError: If the object cannot be serialized

    Returns:
        str: The YAML string.
    """
    if encode is None:
        encode = ENCODE_YAML

    if is_json_annotation(annotation):
        type_annotation, json_annotation = get_json_annotation(annotation)
    else:
        type_annotation, json_annotation = annotation, JSONValue()

    json_obj = from_json_value(
        obj,
        type_annotation,
        json_annotation,
        config
    )
    return encode(json_obj)
