"""An untyped serializer"""

import json
from typing import Any, Type

from ..config import SerializerConfig


def _serialize_key_if_str(key: Any, config: SerializerConfig) -> Any:
    return config.serialize_key(
        key
    ) if config.serialize_key and isinstance(key, str) else key


def _from_value(
        value: Any,
        type_annotation: Type,
        config: SerializerConfig
) -> Any:
    serializer = config.value_serializers.get(type_annotation)
    if serializer is not None:
        return serializer(value)
    return value


def _from_list(lst: list, config: SerializerConfig) -> list:
    return [
        _from_any(item, config)
        for item in lst
    ]


def _from_dict(dct: dict, config: SerializerConfig) -> dict:
    return {
        _serialize_key_if_str(key, config): _from_any(value, config)
        for key, value in dct.items()
    }


def _from_any(obj: Any, config: SerializerConfig) -> Any:
    if isinstance(obj, dict):
        return _from_dict(obj, config)
    elif isinstance(obj, list):
        return _from_list(obj, config)
    else:
        return _from_value(obj, type(obj), config)


def serialize(obj: Any, config: SerializerConfig) -> str:
    json_obj = _from_any(obj, config)
    return json.dumps(
        json_obj,
        indent=2 if config.pretty_print else None
    )
