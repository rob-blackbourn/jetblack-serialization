"""JSON serialization"""

from typing import Any

from ..config import SerializerConfig
from ..types import Annotation
from ..utils import is_typed

from .typed_serializer import serialize_typed
from .typed_deserializer import deserialize_typed
from .untyped_serializer import serialize_untyped
from .untyped_deserializer import deserialize_untyped

from .encoding import JSONEncoder, JSONDecoder


def serialize(
        obj: Any,
        annotation: Any,
        config: SerializerConfig | None = None,
        encode: JSONEncoder | None = None
) -> str:
    """Convert the object to JSON

    Args:
        obj (Any): The object to convert
        annotation (Annotation): The type annotation
        config (SerializerConfig): The serializer configuration

    Returns:
        str: The serialized object
    """
    if is_typed(annotation):
        return serialize_typed(obj, annotation, config, encode)
    else:
        return serialize_untyped(obj, config, encode)


def deserialize(
        text: str | bytes | bytearray,
        annotation: Annotation,
        config: SerializerConfig | None = None,
        decode: JSONDecoder | None = None
) -> Any:
    """Convert JSON to an object

    Args:
        text (str | bytes | bytearray): The JSON string
        annotation (Annotation): The type annotation
        config (SerializerConfig): The serializer configuration

    Returns:
        Any: The deserialized object.
    """
    if is_typed(annotation):
        return deserialize_typed(text, annotation, config, decode)
    else:
        return deserialize_untyped(text, config, decode)
