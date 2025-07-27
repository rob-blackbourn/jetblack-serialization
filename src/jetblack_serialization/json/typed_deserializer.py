"""Typed JSON deserialization"""

from decimal import Decimal
from enum import Enum
from inspect import Parameter, isclass
import json
from types import NoneType
from typing import (
    Any,
    Union,
    cast,
    is_typeddict,
    get_args
)

from ..config import BaseSerializerConfig
from ..custom_annotations import get_typed_dict_key_default
from ..typing_ex import (
    get_unannotated,
    is_annotated,
    is_list,
    is_optional,
    is_union,
    typeddict_keys,
)
from ..types import Annotation
from ..utils import is_value_type

from .annotations import (
    JSONAnnotation,
    JSONValue,
    JSONProperty,
    is_json_annotation,
    get_json_annotation
)
from .config import SerializerConfig


def _to_value(
        value: Any,
        type_annotation: type,
        config: BaseSerializerConfig
) -> Any:
    if isinstance(value, type_annotation):
        return value

    if isinstance(value, str):
        if type_annotation is str:
            return value
        elif type_annotation is int:
            return int(value)
        elif type_annotation is bool:
            return value.lower() == 'true'
        elif type_annotation is float:
            return float(value)
        elif type_annotation is Decimal:
            return Decimal(value)
        elif isclass(type_annotation) and issubclass(type_annotation, Enum):
            return type_annotation[value]
        else:
            deserializer = config.value_deserializers.get(type_annotation)
            if deserializer is not None:
                return deserializer(value)
    elif isinstance(value, (int, float)) and type_annotation is Decimal:
        return Decimal(value)

    raise TypeError(f'Unhandled type {type_annotation}')


def _to_optional(
        obj: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: BaseSerializerConfig
) -> Any:
    # An optional is a union where the last element is the None type.
    union_types = [t for t in get_args(type_annotation) if t is not NoneType]
    if len(union_types) == 1:
        return None if not obj else _to_any(
            obj,
            union_types[0],
            json_annotation,
            config
        )
    else:
        union = Union[tuple(union_types)]  # type: ignore
        return _to_any(
            obj,
            union,
            json_annotation,
            config
        )


def _to_list(
        lst: list,
        list_annotation: Annotation,
        config: BaseSerializerConfig
) -> list[Any]:
    item_type_annotation, *_rest = get_args(list_annotation)
    if is_annotated(item_type_annotation):
        item_type_annotation, item_json_annotation = get_json_annotation(
            item_type_annotation
        )
    else:
        item_json_annotation = JSONValue()

    return [
        _to_any(
            item,
            item_type_annotation,
            item_json_annotation,
            config
        )
        for item in lst
    ]


def _to_union(
        obj: dict[str, Any] | None,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: BaseSerializerConfig
) -> Any:
    for item_type_annotation in get_args(type_annotation):
        try:
            return _to_any(
                obj,
                item_type_annotation,
                json_annotation,
                config
            )
        except:  # pylint: disable=bare-except
            pass


def _to_dict(
        obj: dict[str, Any],
        dict_annotation: Annotation,
        config: BaseSerializerConfig
) -> dict[str, Any]:
    json_obj: dict[str, Any] = {}

    typed_dict_keys = typeddict_keys(dict_annotation)
    assert typed_dict_keys is not None
    for key, key_annotation in typed_dict_keys.items():
        default = get_typed_dict_key_default(key_annotation)
        if is_json_annotation(key_annotation):
            item_type_annotation, item_json_annotation = get_json_annotation(
                key_annotation
            )
            if not issubclass(type(item_json_annotation), JSONProperty):
                raise TypeError("Must be a property")
            json_property = cast(JSONProperty, item_json_annotation)
        else:
            tag = config.serialize_key(
                key
            ) if isinstance(key, str) else key
            json_property = JSONProperty(tag)
            item_type_annotation = get_unannotated(key_annotation)

        if json_property.tag in obj:
            json_obj[key] = _to_any(
                obj[json_property.tag],
                item_type_annotation,
                json_property,
                config
            )
        elif default is not Parameter.empty:
            json_obj[key] = _to_any(
                default,
                item_type_annotation,
                json_property,
                config
            )
        elif is_optional(item_type_annotation):
            json_obj[key] = None
        else:
            raise KeyError(
                f'Required key "{json_property.tag}" is missing'
            )

    return json_obj


def _to_any(
        json_value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: BaseSerializerConfig
) -> Any:
    if is_value_type(type_annotation, config.value_deserializers.keys()):
        return _to_value(
            json_value,
            type_annotation,
            config
        )
    elif is_optional(type_annotation):
        return _to_optional(
            json_value,
            type_annotation,
            json_annotation,
            config
        )
    elif is_list(type_annotation):
        return _to_list(
            json_value,
            type_annotation,
            config
        )
    elif is_typeddict(type_annotation):
        return _to_dict(
            json_value,
            type_annotation,
            config
        )
    elif is_union(type_annotation):
        return _to_union(
            json_value,
            type_annotation,
            json_annotation,
            config
        )
    else:
        raise TypeError


def from_json_value(
        config: BaseSerializerConfig,
        json_value: Any,
        annotation: Annotation,
) -> Any:
    """Convert from a json value

    Args:
        config (JSONSerializerConfig): The serializer configuration
        json_value (Any): The JSON value
        annotation (Annotation): The type annotation

    Raises:
        TypeError: If the value cannot be deserialized to the type

    Returns:
        Any: The deserialized value
    """
    if is_json_annotation(annotation):
        type_annotation, json_annotation = get_json_annotation(annotation)
        if not isinstance(json_annotation, JSONValue):
            raise TypeError(
                "Expected the root value to have a JSONValue annotation"
            )
    else:
        type_annotation, json_annotation = annotation, JSONValue()

    return _to_any(
        json_value,
        type_annotation,
        json_annotation,
        config
    )


def deserialize_typed(
        text: Union[str, bytes, bytearray],
        annotation: Annotation,
        config: SerializerConfig
) -> Any:
    """Convert JSON to an object

    Args:
        text (Union[str, bytes, bytearray]): The JSON string
        annotation (str): The type annotation

    Returns:
        Any: The deserialized object.
    """
    to_object = config.to_object or json.loads
    json_value = to_object(text)
    return from_json_value(config, json_value, annotation)
