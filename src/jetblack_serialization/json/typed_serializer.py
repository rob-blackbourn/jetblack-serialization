"""Typed JSON serialization"""

from decimal import Decimal
from enum import Enum
from inspect import Parameter
import json
from typing import Any, Type, Union, cast, get_args, is_typeddict

from ..config import BaseSerializerConfig
from ..types import Annotation
from ..typing_ex import (
    is_annotated,
    typeddict_keys,
    is_optional,
    is_list,
    is_union
)
from ..utils import is_value_type

from .annotations import (
    JSONAnnotation,
    JSONValue,
    JSONProperty,
    is_json_annotation,
    get_json_annotation
)
from .config import SerializerConfig


def _from_value(
        value: Any,
        type_annotation: Type,
        config: BaseSerializerConfig
) -> Any:
    if type_annotation is str:
        return value
    elif type_annotation is int:
        return value
    elif type_annotation is bool:
        return value
    elif type_annotation is float:
        return value
    elif type_annotation is Decimal:
        return float(value)
    elif isinstance(value, Enum):
        return value.name
    else:
        serializer = config.value_serializers.get(type_annotation)
        if serializer is not None:
            return serializer(value)

    raise TypeError(f'Unhandled type {type_annotation}')


def _from_optional(
        obj: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: BaseSerializerConfig
) -> Any:
    if obj is None:
        return None

    # An optional is a union where the last element is the None type.
    union_types = get_args(type_annotation)[:-1]
    if len(union_types) == 1:
        # This was Optional[T]
        return from_json_value(
            obj,
            union_types[0],
            json_annotation,
            config
        )
    else:
        return _from_union(
            obj,
            Union[tuple(union_types)],  # type: ignore
            json_annotation,
            config
        )


def _from_union(
        obj: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: BaseSerializerConfig
) -> Any:
    for element_type in get_args(type_annotation):
        try:
            return from_json_value(
                obj,
                element_type,
                json_annotation,
                config
            )
        except:  # pylint: disable=bare-except
            pass


def _from_list(
        lst: list,
        type_annotation: Annotation,
        config: BaseSerializerConfig
) -> Any:
    item_annotation, *_rest = get_args(type_annotation)
    if is_annotated(item_annotation):
        item_type_annotation, item_json_annotation = get_json_annotation(
            item_annotation
        )
    else:
        item_type_annotation = item_annotation
        item_json_annotation = JSONValue()

    return [
        from_json_value(
            item,
            item_type_annotation,
            item_json_annotation,
            config
        )
        for item in lst
    ]


def _from_typed_dict(
        dct: dict,
        type_annotation: Annotation,
        config: BaseSerializerConfig
) -> dict:
    json_obj = {}

    typed_dict_keys = typeddict_keys(type_annotation)
    assert typed_dict_keys is not None
    for key, key_annotation in typed_dict_keys.items():
        default = getattr(type_annotation, key, Parameter.empty)
        if is_annotated(key_annotation):
            item_type_annotation, item_json_annotation = get_json_annotation(
                key_annotation
            )
            if not issubclass(type(item_json_annotation), JSONProperty):
                raise TypeError("<ust be a property")
            json_property = cast(JSONProperty, item_json_annotation)
        else:
            property_name = config.serialize_key(
                key
            ) if isinstance(key, str) else key
            json_property = JSONProperty(property_name)
            item_type_annotation = key_annotation

        value = dct.get(key, default)
        if value is not Parameter.empty:
            json_obj[json_property.tag] = from_json_value(
                value,
                item_type_annotation,
                json_property,
                config
            )
        else:
            # TODO: Should we throw here?
            pass

    return json_obj


def from_json_value(
        value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: BaseSerializerConfig
) -> Any:
    if is_value_type(type_annotation, config.value_serializers.keys()):
        return _from_value(
            value,
            type_annotation,
            config
        )
    elif is_optional(type_annotation):
        return _from_optional(
            value,
            type_annotation,
            json_annotation,
            config
        )
    elif is_list(type_annotation):
        return _from_list(
            value,
            type_annotation,
            config
        )
    elif is_typeddict(type_annotation):
        return _from_typed_dict(
            value,
            type_annotation,
            config
        )
    elif is_union(type_annotation):
        return _from_union(
            value,
            type_annotation,
            json_annotation,
            config
        )
    else:
        raise TypeError('Unhandled type')


def serialize_typed(
        obj: Any,
        annotation: Annotation,
        config: SerializerConfig
) -> str:
    """Serialize an object to JSON

    Args:
        obj (Any): The object to serialize
        annotation (Annotation): The objects type annotation

    Raises:
        TypeError: If the object cannot be serialized

    Returns:
        str: The JSON string
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
    from_object = config.from_object or json.dumps
    return from_object(json_obj)
