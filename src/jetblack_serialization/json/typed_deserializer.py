"""Typed JSON deserialization"""

from decimal import Decimal
from enum import Enum
from inspect import Parameter, isclass
from types import NoneType
from typing import (
    Any,
    Union,
    cast,
    is_typeddict,
    get_args
)

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..custom_annotations import get_typed_dict_key_default
from ..typing_ex import (
    get_unannotated,
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
from ..types import Annotation
from ..utils import is_value_type

from .annotations import (
    JSONAnnotation,
    JSONValue,
    JSONProperty,
    is_json_annotation,
    get_json_annotation
)
from .encoding import JSONDecoder, DECODE_JSON
from .untyped_deserializer import from_untyped_object


def _to_value(
        json_value: Any,
        type_annotation: type,
        config: SerializerConfig,
) -> Any:
    if isinstance(json_value, type_annotation):
        return json_value

    if isinstance(json_value, str):
        if type_annotation is str:
            return json_value
        elif type_annotation is int:
            return int(json_value)
        elif type_annotation is bool:
            return json_value.lower() == 'true'
        elif type_annotation is float:
            return float(json_value)
        elif type_annotation is Decimal:
            return Decimal(json_value)
        elif isclass(type_annotation) and issubclass(type_annotation, Enum):
            return type_annotation[json_value]
        else:
            deserializer = config.value_deserializers.get(type_annotation)
            if deserializer is not None:
                return deserializer(json_value)
    elif isinstance(json_value, (int, float)) and type_annotation is Decimal:
        return Decimal(json_value)

    raise TypeError(f'Unhandled type {type_annotation}')


def _to_optional(
        json_obj: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    if json_obj is None:
        return None

    union_types = [t for t in get_args(type_annotation) if t is not NoneType]
    union = (
        union_types[0]
        if len(union_types) == 1 else
        Union[tuple(union_types)]
    )

    return _to_any(json_obj, union, json_annotation, config)


def _to_list(
        json_list: list,
        list_annotation: Annotation,
        config: SerializerConfig
) -> list[Any]:
    type_annotation, *_rest = get_args(list_annotation)
    type_annotation = resolve_type(type_annotation)

    if is_annotated(type_annotation):
        type_annotation, json_annotation = get_json_annotation(type_annotation)
    else:
        json_annotation = JSONValue()

    return [
        _to_any(
            item,
            type_annotation,
            json_annotation,
            config
        )
        for item in json_list
    ]


def _to_union(
        json_obj: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    if json_annotation.type_selector is None:
        annotations = get_args(type_annotation)
    else:
        annotations = (
            json_annotation.type_selector(json_obj, type_annotation),
        )

    for item_type_annotation in annotations:
        try:
            return _to_any(
                json_obj,
                item_type_annotation,
                json_annotation,
                config
            )
        except:  # pylint: disable=bare-except
            pass

    raise TypeError("Unable to deserialize union")


def _to_dict(
        json_obj: dict[str, Any],
        dict_annotation: Annotation,
        config: SerializerConfig
) -> dict[str, Any]:
    python_dict: dict[str, Any] = {}

    key_type_annotation, value_type_annotation = get_args(dict_annotation)

    key_type_annotation = resolve_type(key_type_annotation)
    value_type_annotation = resolve_type(value_type_annotation)

    if is_annotated(key_type_annotation):
        key_type_annotation, key_json_annotation = get_json_annotation(
            key_type_annotation
        )
    else:
        key_json_annotation = JSONValue()

    if is_annotated(value_type_annotation):
        value_type_annotation, value_json_annotation = get_json_annotation(
            value_type_annotation
        )
    else:
        value_json_annotation = JSONValue()

    for tag, json_value in json_obj.items():
        key = _to_any(
            tag,
            key_type_annotation,
            key_json_annotation,
            config
        )

        python_dict[key] = _to_any(
            json_value,
            value_type_annotation,
            value_json_annotation,
            config
        )

    return python_dict


def _to_tag(python_key: str, config: SerializerConfig) -> str:
    return (
        config.serialize_key(python_key)
        if isinstance(python_key, str) else
        python_key
    )


def _get_json_annotated_key(
        python_key: str,
        annotation: JSONAnnotation,
        config: SerializerConfig
) -> tuple[type[Any], JSONProperty]:
    type_annotation, json_annotation = get_json_annotation(annotation)

    if isinstance(json_annotation, JSONProperty):
        json_property = cast(JSONProperty, json_annotation)
    elif isinstance(json_annotation, JSONValue):
        tag = _to_tag(python_key, config)
        json_property = JSONProperty(tag, json_annotation.type_selector)
    else:
        raise TypeError("Must be a property")

    return type_annotation, json_property


def _get_json_unannotated_key(
        python_key: str,
        annotation: Annotation,
        config: SerializerConfig
) -> tuple[type[Any], JSONProperty]:
    json_property = JSONProperty(_to_tag(python_key, config))
    type_annotation = get_unannotated(annotation)
    return type_annotation, json_property


def _get_key_annotation(
        python_key: str,
        annotation: Annotation,
        config: SerializerConfig
) -> tuple[type[Any], JSONProperty]:
    if is_json_annotation(annotation):
        return _get_json_annotated_key(python_key, annotation, config)

    return _get_json_unannotated_key(python_key, annotation, config)


def _to_typed_dict(
        json_obj: dict[str, Any],
        dict_annotation: Annotation,
        config: SerializerConfig
) -> dict[str, Any]:
    python_dict: dict[str, Any] = {}

    typed_dict_keys = typeddict_keys(dict_annotation)
    assert typed_dict_keys is not None
    for python_key, info in typed_dict_keys.items():
        default = get_typed_dict_key_default(info.annotation)
        item_annotation, json_property = _get_key_annotation(
            python_key,
            info.annotation,
            config
        )

        if json_property.tag in json_obj:
            python_dict[python_key] = _to_any(
                json_obj[json_property.tag],
                item_annotation,
                json_property,
                config
            )
        elif default is not Parameter.empty:
            python_dict[python_key] = _to_any(
                default,
                item_annotation,
                json_property,
                config
            )
        elif is_optional(item_annotation):
            python_dict[python_key] = None
        elif info.is_required:
            raise KeyError(
                f'Required key "{json_property.tag}" is missing'
            )

    return python_dict


def _to_literal(
        json_value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    literal_values = get_args(type_annotation)
    literal_types = {type(v) for v in literal_values}
    for literal_type in literal_types:
        try:
            result = _to_any(
                json_value,
                literal_type,
                json_annotation,
                config
            )
            if result in literal_values:
                return result
        except:  # pylint: disable=bare-except
            pass

    raise ValueError(f'Value {json_value} not in Literal{literal_values}')


def _to_any(
        json_value: Any,
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    type_annotation = resolve_type(type_annotation)

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
        return _to_typed_dict(
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
    elif is_dict(type_annotation):
        return _to_dict(
            json_value,
            type_annotation,
            config
        )
    elif is_literal(type_annotation):
        return _to_literal(
            json_value,
            type_annotation,
            json_annotation,
            config
        )
    elif is_any(type_annotation):
        return from_untyped_object(json_value, config)
    else:
        raise TypeError


def from_json_value(
        json_value: Any,
        annotation: Annotation,
        config: SerializerConfig,
) -> Any:
    """Convert from a json value

    Args:
        json_value (Any): The JSON value
        annotation (Annotation): The type annotation
        config (SerializerConfig): The serializer configuration

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
        config: SerializerConfig | None = None,
        decode: JSONDecoder | None = None
) -> Any:
    """Convert JSON to an object

    Args:
        text (Union[str, bytes, bytearray]): The JSON string
        annotation (str): The type annotation

    Returns:
        Any: The deserialized object.
    """
    json_value = (decode or DECODE_JSON)(text)
    return from_json_value(json_value, annotation, config or DEFAULT_CONFIG)
