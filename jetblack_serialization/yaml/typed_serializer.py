"""A YAML serializer"""

from typing import Any, Type, Union

import yaml

from ..config import SerializerConfig
from ..types import Annotation

from ..json.annotations import is_json_annotation, get_json_annotation, JSONValue
from ..json.typed_serializer import from_json_value

_Dumper = Union[yaml.BaseDumper, yaml.Dumper, yaml.SafeDumper]


def serialize_typed(
        obj: Any,
        annotation: Annotation,
        config: SerializerConfig,
        *,
        dumper: Type[_Dumper] = yaml.SafeDumper
) -> str:
    """Serialize an object to YAML.

    Args:
        obj (Any): The object to serialize.
        annotation (Annotation): The objects type annotation.

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
        Dumper=dumper
    )
