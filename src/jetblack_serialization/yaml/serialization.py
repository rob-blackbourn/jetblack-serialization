"""YAML serialization"""

from typing import Any, AnyStr

from ..types import (
    Annotation,
)
from ..utils import is_typed

from .config import SerializerConfig
from .typed_serializer import serialize_typed
from .typed_deserializer import deserialize_typed
from .untyped_serializer import serialize_untyped
from .untyped_deserializer import deserialize_untyped


def serialize(
        obj: Any,
        annotation: Any,
        config: SerializerConfig
) -> str:
    """Convert the object to YAML.

    Args:
        obj (Any): The object to convert
        annotation (Annotation): The type annotation
        config (YAMLSerializerConfig): The serializer configuration

    Returns:
        str: The serialized object
    """
    if is_typed(annotation):
        return serialize_typed(obj, annotation, config)
    else:
        return serialize_untyped(obj, config)


def deserialize(
        text: AnyStr,
        annotation: Annotation,
        config: SerializerConfig
) -> Any:
    """Convert YAML to an object.

    Args:
        text (AnyStr): The JSON string
        annotation (Annotation): The type annotation
        config (YAMLSerializerConfig): The serializer configuration

    Returns:
        Any: The deserialized object.
    """
    if is_typed(annotation):
        return deserialize_typed(text, annotation, config)
    else:
        return deserialize_untyped(text, config)
