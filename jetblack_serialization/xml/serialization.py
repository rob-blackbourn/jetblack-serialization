"""Serialization"""

from typing import Any

import jetblack_serialization.typing_inspect_ex as typing_inspect

from ..types import (
    Annotation,
)
from ..config import SerializerConfig


from .typed_xml_serializer import serialize_typed_xml
from .typed_xml_deserializer import deserialize_typed_xml
from .untyped_xml_serializer import serialize_untyped_xml
from .untyped_xml_deserializer import deserialize_untyped_xml


def _is_typed(annotation: Annotation) -> bool:
    return (
        typing_inspect.is_typed_dict_type(annotation) or
        (
            typing_inspect.is_list_type(annotation) and
            _is_typed(typing_inspect.get_args(annotation)[0])
        ) or
        (
            typing_inspect.is_annotated_type(annotation) and
            _is_typed(typing_inspect.get_origin(annotation))
        )
    )


def serialize(
        obj: Any,
        annotation: Any,
        config: SerializerConfig
) -> str:
    """Convert the object to JSON

    Args:
        obj (Any): The object to convert
        annotation (Annotation): The type annotation
        config (SerializerConfig): The serializer configuration

    Returns:
        str: The serialized object
    """
    if _is_typed(annotation):
        return serialize_typed_xml(obj, annotation, config)
    else:
        return serialize_untyped_xml(obj, config)


def deserialize(
        text: str,
        annotation: Annotation,
        config: SerializerConfig,
) -> Any:
    """Convert XML to an object

    Args:
        text (str): The XML string
        annotation (Annotation): The type annotation
        config (SerializerConfig): The serializer configuration

    Returns:
        Any: The deserialized object.
    """
    if _is_typed(annotation):
        return deserialize_typed_xml(text, annotation, config)
    else:
        return deserialize_untyped_xml(text, config)
