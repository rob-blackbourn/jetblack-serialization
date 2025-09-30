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
        config: SerializerConfig
) -> Any:
    if python_value is None:
        return None

    union_types = [t for t in get_args(type_annotation) if t is not NoneType]
    assert len(union_types) == 1, "union types are not supported"
    value_type = union_types[0]
    return from_csv_value(
        python_value,
        value_type,
        config
    )


def _from_list(
        python_list: list,
        list_annotation: Annotation,
        config: SerializerConfig
) -> Any:
    type_annotation, *_rest = get_args(list_annotation)
    type_annotation = resolve_type(type_annotation)

    return [
        from_csv_value(
            item,
            type_annotation,
            config
        )
        for item in python_list
    ]


def _to_csv_key(python_key: str, config: SerializerConfig) -> str:
    return (
        config.serialize_key(python_key)
        if isinstance(python_key, str) else
        python_key
    )


def _get_csv_key(
        python_key: str,
        annotation: Annotation,
        config: SerializerConfig
) -> tuple[Annotation, str]:
    tag = _to_csv_key(python_key, config)
    return annotation, tag


def _from_typed_dict(
        python_dict: dict,
        dict_annotation: Annotation,
        config: SerializerConfig
) -> list[Any]:
    row = list[Any]()

    typed_dict_keys = typeddict_keys(dict_annotation)
    for python_key, info in typed_dict_keys.items():
        default = getattr(dict_annotation, python_key, Parameter.empty)
        item_annotation, csv_key = _get_csv_key(
            python_key,
            info.annotation,
            config
        )

        csv_value = python_dict.get(python_key, default)
        if csv_value is not Parameter.empty:
            row.append(
                from_csv_value(
                    csv_value,
                    item_annotation,
                    config
                )
            )
        elif not info.is_required:
            row.append(None)
        else:
            raise KeyError(f'Missing required property {python_key}')

    return row


def _from_literal(
        python_value: Any,
        type_annotation: Annotation,
        config: SerializerConfig
) -> Any:
    literal_values = get_args(type_annotation)
    literal_types = {type(v) for v in literal_values}
    for literal_type in literal_types:
        try:
            result = from_csv_value(
                python_value,
                literal_type,
                config
            )
            if result in literal_values:
                return result
        except:  # pylint: disable=bare-except
            pass

    raise ValueError(f'Value {python_value} not in Literal{literal_values}')


def from_csv_value(
        python_value: Any,
        type_annotation: Annotation,
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
        raise ValueError("union types are not supported")
    elif is_dict(type_annotation):
        raise ValueError("untyped dicts are not supported")
    elif is_literal(type_annotation):
        return _from_literal(
            python_value,
            type_annotation,
            config
        )
    elif is_any(type_annotation):
        raise ValueError("The Any type is not supported")
    else:
        raise TypeError('Unhandled type')
