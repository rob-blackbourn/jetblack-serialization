"""An XML serializer"""

from decimal import Decimal
from inspect import Parameter
import json
from typing import Any, Type, Union, cast

import jetblack_serialization.typing_inspect_ex as typing_inspect
from ..config import SerializerConfig
from ..types import Annotation
from ..utils import is_simple_type

from .annotations import (
    JSONAnnotation,
    JSONValue,
    JSONProperty,
    is_json_annotation,
    get_json_annotation
)


def _from_value(
        value: Any,
        type_annotation: Type,
        config: SerializerConfig
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
    else:
        serializer = config.value_serializers.get(type_annotation)
        if serializer is not None:
            return serializer(value)

    raise TypeError(f'Unhandled type {type_annotation}')


def _from_optional(
        obj: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    if obj is None:
        return None

    # An optional is a union where the last element is the None type.
    union_types = typing_inspect.get_args(type_annotation)[:-1]
    if len(union_types) == 1:
        # This was Optional[T]
        return _from_any(
            obj,
            union_types[0],
            json_annotation,
            config
        )
    else:
        return _from_union(
            obj,
            Union[tuple(union_types)],
            json_annotation,
            config
        )


def _from_union(
        obj: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    for element_type in typing_inspect.get_args(type_annotation):
        try:
            return _from_any(
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
        config: SerializerConfig
) -> Any:
    item_annotation, *_rest = typing_inspect.get_args(type_annotation)
    if typing_inspect.is_annotated_type(item_annotation):
        item_type_annotation, item_json_annotation = get_json_annotation(
            item_annotation
        )
    else:
        item_type_annotation = item_annotation
        item_json_annotation = JSONValue()

    return [
        _from_any(
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
        config: SerializerConfig
) -> dict:
    json_obj = dict()

    typed_dict_keys = typing_inspect.typed_dict_keys(type_annotation)
    for key, key_annotation in typed_dict_keys.items():
        default = getattr(type_annotation, key, Parameter.empty)
        if typing_inspect.is_annotated_type(key_annotation):
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
        if value != Parameter.empty:
            json_obj[json_property.tag] = _from_any(
                value,
                item_type_annotation,
                json_property,
                config
            )
        else:
            # TODO: Should we throw here?
            pass

    return json_obj


def _from_any(
        value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    if is_simple_type(type_annotation):
        return _from_value(
            value,
            type_annotation,
            config
        )
    elif typing_inspect.is_optional_type(type_annotation):
        return _from_optional(
            value,
            type_annotation,
            json_annotation,
            config
        )
    elif typing_inspect.is_list_type(type_annotation):
        return _from_list(
            value,
            type_annotation,
            config
        )
    elif typing_inspect.is_typed_dict_type(type_annotation):
        return _from_typed_dict(
            value,
            type_annotation,
            config
        )
    elif typing_inspect.is_union_type(type_annotation):
        return _from_union(
            value,
            type_annotation,
            json_annotation,
            config
        )
    else:
        raise TypeError('Unhandled type')


def serialize(
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

    json_obj = _from_any(
        obj,
        type_annotation,
        json_annotation,
        config
    )
    return json.dumps(
        json_obj,
        indent=2 if config.pretty_print else None
    )
