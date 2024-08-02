"""Untyped JSON serialization"""

import json
from typing import Any, Type

from ..config import BaseSerializerConfig

from .config import SerializerConfig


def _serialize_key_if_str(key: Any, config: BaseSerializerConfig) -> Any:
    return config.serialize_key(
        key
    ) if config.serialize_key is not None and isinstance(key, str) else key


def _from_value(
        value: Any,
        type_annotation: Type,
        config: BaseSerializerConfig
) -> Any:
    serializer = config.value_serializers.get(type_annotation)
    if serializer is not None:
        return serializer(value)
    return value


def _from_list(lst: list, config: BaseSerializerConfig) -> list:
    return [
        from_untyped_object(item, config)
        for item in lst
    ]


def _from_dict(dct: dict, config: BaseSerializerConfig) -> dict:
    return {
        _serialize_key_if_str(key, config): from_untyped_object(value, config)
        for key, value in dct.items()
    }


def from_untyped_object(obj: Any, config: BaseSerializerConfig) -> Any:
    if isinstance(obj, dict):
        return _from_dict(obj, config)
    elif isinstance(obj, list):
        return _from_list(obj, config)
    else:
        return _from_value(obj, type(obj), config)


def serialize_untyped(obj: Any, config: SerializerConfig) -> str:
    json_obj = from_untyped_object(obj, config)
    return json.dumps(
        json_obj,
        indent=2 if config.pretty_print else None
    )
