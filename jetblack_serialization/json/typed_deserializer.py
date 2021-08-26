"""JSON Serialization"""

from decimal import Decimal
from inspect import Parameter
import json
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    cast
)

from .. import typing_inspect_ex as typing_inspect
from ..config import SerializerConfig
from ..custom_annotations import get_typed_dict_key_default
from ..types import Annotation
from ..utils import is_simple_type

from .annotations import (
    JSONAnnotation,
    JSONValue,
    JSONProperty,
    is_json_annotation,
    get_json_annotation
)


def _to_value(
        value: Any,
        type_annotation: Type,
        config: SerializerConfig
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
        config: SerializerConfig
) -> Any:
    # An optional is a union where the last element is the None type.
    union_types = typing_inspect.get_args(type_annotation)[:-1]
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
        config: SerializerConfig
) -> List[Any]:
    item_type_annotation, *_rest = typing_inspect.get_args(list_annotation)
    if typing_inspect.is_annotated_type(item_type_annotation):
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
        obj: Optional[Dict[str, Any]],
        type_annotation: Annotation,
        json_annotation: JSONAnnotation,
        config: SerializerConfig
) -> Any:
    for item_type_annotation in typing_inspect.get_args(type_annotation):
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
        obj: Dict[str, Any],
        dict_annotation: Annotation,
        config: SerializerConfig
) -> Dict[str, Any]:
    json_obj: Dict[str, Any] = {}

    typed_dict_keys = typing_inspect.typed_dict_keys(dict_annotation)
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
            item_type_annotation = typing_inspect.get_unannotated_type(
                key_annotation
            )

        if json_property.tag in obj:
            json_obj[key] = _to_any(
                obj[json_property.tag],
                item_type_annotation,
                json_property,
                config
            )
        elif default != Parameter.empty:
            json_obj[key] = _to_any(
                default,
                item_type_annotation,
                json_property,
                config
            )
        elif typing_inspect.is_optional_type(item_type_annotation):
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
        config: SerializerConfig
) -> Any:
    if is_simple_type(type_annotation):
        return _to_value(
            json_value,
            type_annotation,
            config
        )
    elif typing_inspect.is_optional_type(type_annotation):
        return _to_optional(
            json_value,
            type_annotation,
            json_annotation,
            config
        )
    elif typing_inspect.is_list_type(type_annotation):
        return _to_list(
            json_value,
            type_annotation,
            config
        )
    elif typing_inspect.is_typed_dict_type(type_annotation):
        return _to_dict(
            json_value,
            type_annotation,
            config
        )
    elif typing_inspect.is_union_type(type_annotation):
        return _to_union(
            json_value,
            type_annotation,
            json_annotation,
            config
        )
    else:
        raise TypeError


def from_json_value(
        config: SerializerConfig,
        json_value: Any,
        annotation: Annotation,
) -> Any:
    """Convert from a json value

    Args:
        config (SerializerConfig): The serialier configuration
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


def deserialize(
        text: str,
        annotation: Annotation,
        config: SerializerConfig
) -> Any:
    """Convert JSON to an object

    Args:
        text (str): The JSON string
        annotation (str): The type annotation

    Returns:
        Any: The deserialized object.
    """
    json_value = json.loads(text)
    return from_json_value(config, json_value, annotation)
