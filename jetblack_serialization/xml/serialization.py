"""XML serialization"""

from typing import Any, AnyStr

from ..types import Annotation
from ..utils import is_typed

from .config import XMLSerializerConfig
from .typed_serializer import serialize_typed
from .typed_deserializer import deserialize_typed
from .untyped_serializer import serialize_untyped
from .untyped_deserializer import deserialize_untyped


def serialize(
        obj: Any,
        annotation: Any,
        config: XMLSerializerConfig
) -> str:
    """Convert the object to JSON

    Args:
        obj (Any): The object to convert
        annotation (Annotation): The type annotation
        config (XMLSerializerConfig): The serializer configuration

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
        config: XMLSerializerConfig,
) -> Any:
    """Convert XML to an object

    Args:
        text (str): The XML string
        annotation (Annotation): The type annotation
        config (XMLSerializerConfig): The serializer configuration

    Returns:
        Any: The deserialized object.
    """
    if is_typed(annotation):
        return deserialize_typed(text, annotation, config)
    else:
        return deserialize_untyped(text, config)
