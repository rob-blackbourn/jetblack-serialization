"""Typed JSON serialization"""

from decimal import Decimal
from enum import Enum
from inspect import Parameter
from typing import Any, Type, Union, cast, get_args, is_typeddict

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..types import Annotation
from ..typing_ex import (
    is_annotated,
    is_dict,
    is_list,
    is_literal,
    is_optional,
    is_union,
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
        config: SerializerConfig
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
        config: SerializerConfig
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
        list_annotation: Annotation,
        config: SerializerConfig
) -> Any:
    item_annotation, *_rest = get_args(list_annotation)
    if is_annotated(item_annotation):
        type_annotation, json_annotation = get_json_annotation(item_annotation)
    else:
        type_annotation = item_annotation
        json_annotation = JSONValue()

    return [
        from_json_value(
            item,
            type_annotation,
            json_annotation,
            config
        )
        for item in lst
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
        dct: dict,
        dict_annotation: Annotation,
        config: SerializerConfig
) -> dict:
    json_obj: dict[str, Any] = {}

    typed_dict_keys = typeddict_keys(dict_annotation)
    assert typed_dict_keys is not None
    for python_key, info in typed_dict_keys.items():
        default = getattr(dict_annotation, python_key, Parameter.empty)
        item_annotation, json_property = _get_annotated_key(
            python_key,
            info.annotation,
            config
        )

        json_value = dct.get(python_key, default)
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
        dct: dict,
        type_annotation: Annotation,
        config: SerializerConfig
) -> dict:
    json_obj = {}

    item_annotation, *_rest = get_args(type_annotation)
    if is_annotated(item_annotation):
        item_type_annotation, item_json_annotation = get_json_annotation(
            item_annotation
        )
    else:
        item_type_annotation = item_annotation
        item_json_annotation = JSONValue()

    for key, item in dct.items():
        json_obj[key] = from_json_value(
            item,
            item_type_annotation,
            item_json_annotation,
            config
        )

    return json_obj


def _from_literal(
        value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    literal_values = get_args(type_annotation)
    literal_types = {type(v) for v in literal_values}
    for literal_type in literal_types:
        try:
            result = from_json_value(
                value,
                literal_type,
                json_annotation,
                config
            )
            if result in literal_values:
                return result
        except:  # pylint: disable=bare-except
            pass

    raise ValueError(f'Value {value} not in Literal{literal_values}')


def from_json_value(
        value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
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
    elif is_dict(type_annotation):
        return _from_dict(
            value,
            type_annotation,
            config
        )
    elif is_literal(type_annotation):
        return _from_literal(
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
        config: SerializerConfig | None = None,
        encode: JSONEncoder | None = None
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
        config or DEFAULT_CONFIG
    )
    return (encode or ENCODE_JSON)(json_obj)
