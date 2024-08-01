"""YAML serialization"""

from typing import Any, Type, Union

import yaml

from .. import typing_inspect_ex as typing_inspect
from ..types import (
    Annotation,
)
from ..config import SerializerConfig


from .typed_serializer import serialize_typed, _Dumper
from .typed_deserializer import deserialize_typed, _Loader


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
        config: SerializerConfig,
        *,
        dumper: Type[_Dumper] = yaml.SafeDumper
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
        return serialize_typed(obj, annotation, config, dumper=dumper)
    else:
        return yaml.dump(obj, Dumper=dumper)


def deserialize(
        text: Union[str, bytes, bytearray],
        annotation: Annotation,
        config: SerializerConfig,
        *,
        loader: Type[_Loader] = yaml.SafeLoader
) -> Any:
    """Convert JSON to an object

    Args:
        text (Union[str, bytes, bytearray]): The JSON string
        annotation (Annotation): The type annotation
        config (SerializerConfig): The serializer configuration

    Returns:
        Any: The deserialized object.
    """
    if _is_typed(annotation):
        return deserialize_typed(text, annotation, config)
    else:
        return yaml.load(text, Loader=loader)
