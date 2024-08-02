"""Typed YAML serialization"""

from typing import Any

import yaml

from ..types import Annotation

from ..json.annotations import is_json_annotation, get_json_annotation, JSONValue
from ..json.typed_serializer import from_json_value

from .config import YAMLSerializerConfig


def serialize_typed(
        obj: Any,
        annotation: Annotation,
        config: YAMLSerializerConfig
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
    return yaml.dump(
        json_obj,
        Dumper=config.dumper
    )
