"""Typed JSON serialization"""

from decimal import Decimal
from enum import Enum
from inspect import Parameter
from types import NoneType
from typing import Any, Type, Union, cast, get_args, is_typeddict

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..types import Annotation
from ..typing_ex import (
    is_annotated,
    is_any,
    is_dict,
    is_list,
    is_literal,
    is_optional,
    is_union,
    resolve_type,
    typeddict_keys,
)
from ..utils import is_value_type

from .annotations import (
    JSONAnnotation,
    JSONValue,
    JSONProperty,
    is_json_annotation,
    get_json_annotation
)
from .encoding import JSONEncoder, ENCODE_JSON
from .untyped_serializer import from_untyped_object


def _from_value(
        python_value: Any,
        type_annotation: Type,
        config: SerializerConfig
) -> Any:
    if type_annotation is str:
        return python_value
    elif type_annotation is int:
        return python_value
    elif type_annotation is bool:
        return python_value
    elif type_annotation is float:
        return python_value
    elif type_annotation is Decimal:
        return float(python_value)
    elif isinstance(python_value, Enum):
        return python_value.name
    else:
        serializer = config.value_serializers.get(type_annotation)
        if serializer is not None:
            return serializer(python_value)

    raise TypeError(f'Unhandled type {type_annotation}')


def _from_optional(
        python_value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    if python_value is None:
        return None

    union_types = [t for t in get_args(type_annotation) if t is not NoneType]
    if len(union_types) == 1:
        return from_json_value(
            python_value,
            union_types[0],
            json_annotation,
            config
        )

    return _from_union(
        python_value,
        Union[tuple(union_types)],  # type: ignore
        json_annotation,
        config
    )


def _from_union(
        python_value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    for element_type in get_args(type_annotation):
        try:
            return from_json_value(
                python_value,
                element_type,
                json_annotation,
                config
            )
        except:  # pylint: disable=bare-except
            pass

    raise TypeError("Unable to serialize union")


def _from_list(
        python_list: list,
        list_annotation: Annotation,
        config: SerializerConfig
) -> Any:
    type_annotation, *_rest = get_args(list_annotation)
    type_annotation = resolve_type(type_annotation)
    if is_annotated(type_annotation):
        type_annotation, json_annotation = get_json_annotation(type_annotation)
    else:
        json_annotation = JSONValue()

    return [
        from_json_value(
            item,
            type_annotation,
            json_annotation,
            config
        )
        for item in python_list
    ]


def _to_tag(python_key: str, config: SerializerConfig) -> str:
    return (
        config.serialize_key(python_key)
        if isinstance(python_key, str) else
        python_key
    )


def _get_json_annotated_key(
        python_key: str,
        annotation: Annotation,
        config: SerializerConfig
) -> tuple[Annotation, JSONProperty]:
    type_annotation, json_annotation = get_json_annotation(annotation)
    if isinstance(json_annotation, JSONProperty):
        json_annotation = cast(JSONProperty, json_annotation)
    elif isinstance(json_annotation, JSONValue):
        tag = _to_tag(python_key, config)
        json_annotation = JSONProperty(tag, json_annotation.type_selector)
    else:
        raise TypeError("must be a property")

    return type_annotation, json_annotation


def _get_json_unannotated_key(
        python_key: str,
        annotation: Annotation,
        config: SerializerConfig
) -> tuple[Annotation, JSONProperty]:
    return annotation, JSONProperty(_to_tag(python_key, config))


def _get_annotated_key(
        python_key: str,
        annotation: Annotation,
        config: SerializerConfig
) -> tuple[Annotation, JSONProperty]:
    if is_json_annotation(annotation):
        return _get_json_annotated_key(python_key, annotation, config)

    return _get_json_unannotated_key(python_key, annotation, config)


def _from_typed_dict(
        python_dict: dict,
        dict_annotation: Annotation,
        config: SerializerConfig
) -> dict:
    json_obj: dict[str, Any] = {}

    typed_dict_keys = typeddict_keys(dict_annotation)
    for python_key, info in typed_dict_keys.items():
        default = getattr(dict_annotation, python_key, Parameter.empty)
        item_annotation, json_property = _get_annotated_key(
            python_key,
            info.annotation,
            config
        )

        json_value = python_dict.get(python_key, default)
        if json_value is not Parameter.empty:
            json_obj[json_property.tag] = from_json_value(
                json_value,
                item_annotation,
                json_property,
                config
            )
        elif info.is_required:
            raise KeyError(f'Missing required property {python_key}')

    return json_obj


def _from_dict(
        python_dict: dict,
        type_annotation: Annotation,
        config: SerializerConfig
) -> dict:
    json_obj: dict[str, Any] = {}

    item_annotation, *_rest = get_args(type_annotation)
    item_annotation = resolve_type(item_annotation)
    if is_annotated(item_annotation):
        item_type_annotation, item_json_annotation = get_json_annotation(
            item_annotation
        )
    else:
        item_type_annotation = item_annotation
        item_json_annotation = JSONValue()

    for key, item in python_dict.items():
        tag = _to_tag(key, config)
        json_obj[tag] = from_json_value(
            item,
            item_type_annotation,
            item_json_annotation,
            config
        )

    return json_obj


def _from_literal(
        python_value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    literal_values = get_args(type_annotation)
    literal_types = {type(v) for v in literal_values}
    for literal_type in literal_types:
        try:
            result = from_json_value(
                python_value,
                literal_type,
                json_annotation,
                config
            )
            if result in literal_values:
                return result
        except:  # pylint: disable=bare-except
            pass

    raise ValueError(f'Value {python_value} not in Literal{literal_values}')


def from_json_value(
        python_value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    type_annotation = resolve_type(type_annotation)

    if is_value_type(type_annotation, config.value_serializers.keys()):
        return _from_value(
            python_value,
            type_annotation,
            config
        )
    elif is_optional(type_annotation):
        return _from_optional(
            python_value,
            type_annotation,
            json_annotation,
            config
        )
    elif is_list(type_annotation):
        return _from_list(
            python_value,
            type_annotation,
            config
        )
    elif is_typeddict(type_annotation):
        return _from_typed_dict(
            python_value,
            type_annotation,
            config
        )
    elif is_union(type_annotation):
        return _from_union(
            python_value,
            type_annotation,
            json_annotation,
            config
        )
    elif is_dict(type_annotation):
        return _from_dict(
            python_value,
            type_annotation,
            config
        )
    elif is_literal(type_annotation):
        return _from_literal(
            python_value,
            type_annotation,
            json_annotation,
            config
        )
    elif is_any(type_annotation):
        return from_untyped_object(
            python_value,
            config
        )
    else:
        raise TypeError('Unhandled type')


def serialize_typed(
        python_obj: Any,
        annotation: Annotation,
        config: SerializerConfig | None = None,
        encode: JSONEncoder | None = None
) -> str:
    """Serialize an object to JSON

    Args:
        python_obj (Any): The object to serialize
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
        python_obj,
        type_annotation,
        json_annotation,
        config or DEFAULT_CONFIG
    )
    return (encode or ENCODE_JSON)(json_obj)
