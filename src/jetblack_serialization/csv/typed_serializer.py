"""Typed JSON serialization"""

from enum import Enum
from inspect import Parameter
from types import NoneType
from typing import Any, Type, get_args, is_typeddict

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..types import Annotation
from ..typing_ex import (
    is_any,
    is_dict,
    is_list,
    is_literal,
    is_optional,
    is_union,
    get_optional_type,
    resolve_type,
    typeddict_keys,
)
from ..utils import is_value_type

from .encoding import ENCODE_CSV, CSVEncoder


def _from_value(
        python_value: Any,
        type_annotation: Type,
        config: SerializerConfig
) -> str:
    if type_annotation is str:
        return python_value
    elif type_annotation is int:
        return str(python_value)
    elif type_annotation is bool:
        return 'true' if python_value else 'false'
    elif type_annotation is float:
        return str(python_value)
    elif isinstance(python_value, Enum):
        return python_value.name
    else:
        serializer = config.value_serializers.get(type_annotation)
        if serializer is not None:
            return str(serializer(python_value))

    raise TypeError(f'Unhandled type {type_annotation}')


def _from_optional(
        python_value: Any,
        type_annotation: Annotation,
        config: SerializerConfig
) -> str | list[str]:
    if python_value is None:
        return ''

    union_types = [t for t in get_args(type_annotation) if t is not NoneType]
    assert len(union_types) == 1, "union types are not supported"
    value_type = union_types[0]
    return from_csv_value(
        python_value,
        value_type,
        config
    )


def _from_typed_dict(
        python_dict: dict,
        dict_annotation: Annotation,
        config: SerializerConfig
) -> list[str]:
    row = list[str]()

    typed_dict_keys = typeddict_keys(dict_annotation)
    for python_key, info in typed_dict_keys.items():
        default = getattr(dict_annotation, python_key, Parameter.empty)

        csv_value = python_dict.get(python_key, default)
        if csv_value is not Parameter.empty:
            value = from_csv_value(
                csv_value,
                info.annotation,
                config
            )
            if isinstance(value, list):
                row.extend(value)
            else:
                row.append(value)
        elif not info.is_required:
            row.append('')
        else:
            raise KeyError(f'Missing required property {python_key}')

    return row


def _from_literal(
        python_value: Any,
        type_annotation: Annotation,
        config: SerializerConfig
) -> str:
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
                return str(result)
        except:  # pylint: disable=bare-except
            pass

    raise ValueError(f'Value {python_value} not in Literal{literal_values}')


def from_csv_value(
        python_value: Any,
        type_annotation: Annotation,
        config: SerializerConfig
) -> str | list[str]:
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
    elif is_typeddict(type_annotation):
        return _from_typed_dict(
            python_value,
            type_annotation,
            config
        )
    elif is_literal(type_annotation):
        return _from_literal(
            python_value,
            type_annotation,
            config
        )
    elif is_list(type_annotation):
        raise ValueError("lists are not supported")
    elif is_union(type_annotation):
        raise ValueError("union types are not supported")
    elif is_dict(type_annotation):
        raise ValueError("untyped dicts are not supported")
    elif is_any(type_annotation):
        raise ValueError("The Any type is not supported")
    else:
        raise TypeError('Unhandled type')


def _serialize_header(
        prefix: str,
        typed_dict_annotation: Annotation,
        config: SerializerConfig
) -> list[str]:
    headers = list[str]()

    typed_dict_keys = typeddict_keys(typed_dict_annotation)
    for python_key, info in typed_dict_keys.items():
        key_annotation = resolve_type(info.annotation)

        if is_optional(key_annotation):
            key_annotation = get_optional_type(key_annotation)

        csv_key = prefix + python_key

        if is_value_type(key_annotation):
            headers.append(csv_key)
        elif is_typeddict(key_annotation):
            headers.extend(
                _serialize_header(
                    csv_key + ".",
                    info.annotation,
                    config
                )
            )
        else:
            raise ValueError("Unsupported type for header")

    return headers


def serialize_header(
        type_annotation: Annotation,
        config: SerializerConfig
) -> list[str]:
    type_annotation = resolve_type(type_annotation)

    if is_optional(type_annotation):
        type_annotation = get_optional_type(type_annotation)

    assert is_typeddict(type_annotation), "header must be a typed dictionary"

    return _serialize_header('', type_annotation, config)


def serialize_data(
        python_list: Any,
        type_annotation: Annotation,
        config: SerializerConfig
) -> list[list[str]]:
    values = list[list[str]]()

    for python_obj in python_list:
        value = from_csv_value(
            python_obj,
            type_annotation,
            config
        )
        assert isinstance(value, list), "expected a list"
        values.append(value)

    return values


def serialize_typed(
        python_obj: Any,
        annotation: Annotation,
        config: SerializerConfig | None = None,
        encode: CSVEncoder | None = None
) -> str:
    list_annotation = resolve_type(annotation)
    if not is_list(list_annotation):
        raise ValueError("list required")

    type_annotations = get_args(list_annotation)
    if len(type_annotations) != 1:
        raise ValueError("expected a single list type")

    type_annotation = type_annotations[0]

    if config is None:
        config = DEFAULT_CONFIG
    if encode is None:
        encode = ENCODE_CSV

    header = serialize_header(type_annotation, config)
    data = serialize_data(python_obj, type_annotation, config)
    rows = [header] + data
    return ENCODE_CSV(rows)
