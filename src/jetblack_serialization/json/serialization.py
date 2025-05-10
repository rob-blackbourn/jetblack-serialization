"""JSON serialization"""

from typing import Any, Union

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
    """Convert the object to JSON

    Args:
        obj (Any): The object to convert
        annotation (Annotation): The type annotation
        config (JSONSerializerConfig): The serializer configuration

    Returns:
        str: The serialized object
    """
    if is_typed(annotation):
        return serialize_typed(obj, annotation, config)
    else:
        return serialize_untyped(obj, config)


def deserialize(
        text: Union[str, bytes, bytearray],
        annotation: Annotation,
        config: SerializerConfig,
) -> Any:
    """Convert JSON to an object

    Args:
        text (Union[str, bytes, bytearray]): The JSON string
        annotation (Annotation): The type annotation
        config (JSONSerializerConfig): The serializer configuration

    Returns:
        Any: The deserialized object.
    """
    if is_typed(annotation):
        return deserialize_typed(text, annotation, config)
    else:
        return deserialize_untyped(text, config)
