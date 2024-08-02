"""YAML serialization"""

from typing import Any, AnyStr, Type

import yaml

from .. import typing_inspect_ex as typing_inspect
from ..types import (
    Annotation,
)

from .config import YAMLSerializerConfig
from .typed_serializer import serialize_typed
from .typed_deserializer import deserialize_typed
from .untyped_serializer import serialize_untyped
from .untyped_deserializer import deserialize_untyped
from .types import _Loader, _Dumper


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
        config: YAMLSerializerConfig,
        *,
        dumper: Type[_Dumper] = yaml.SafeDumper
) -> str:
    """Convert the object to YAML.

    Args:
        obj (Any): The object to convert
        annotation (Annotation): The type annotation
        config (YAMLSerializerConfig): The serializer configuration

    Returns:
        str: The serialized object
    """
    if _is_typed(annotation):
        return serialize_typed(obj, annotation, config, dumper=dumper)
    else:
        return serialize_untyped(obj, config, dumper=dumper)


def deserialize(
        text: AnyStr,
        annotation: Annotation,
        config: YAMLSerializerConfig,
        *,
        loader: Type[_Loader] = yaml.SafeLoader
) -> Any:
    """Convert YAML to an object.

    Args:
        text (AnyStr): The JSON string
        annotation (Annotation): The type annotation
        config (YAMLSerializerConfig): The serializer configuration

    Returns:
        Any: The deserialized object.
    """
    if _is_typed(annotation):
        return deserialize_typed(text, annotation, config)
    else:
        return deserialize_untyped(text, config, loader=loader)
