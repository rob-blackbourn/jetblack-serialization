"""Untyped JSON serialization"""

from typing import Any

from ..config import SerializerConfig, DEFAULT_CONFIG

from .encoding import JSONEncoder, ENCODE_JSON


def _serialize_key_if_str(key: Any, config: SerializerConfig) -> Any:
    return config.serialize_key(
        key
    ) if config.serialize_key is not None and isinstance(key, str) else key


def _from_value(
        value: Any,
        type_annotation: type,
        config: SerializerConfig
) -> Any:
    serializer = config.value_serializers.get(type_annotation)
    if serializer is not None:
        return serializer(value)
    return value


def _from_list(lst: list, config: SerializerConfig) -> list:
    return [
        from_untyped_object(item, config)
        for item in lst
    ]


def _from_dict(dct: dict, config: SerializerConfig) -> dict:
    return {
        _serialize_key_if_str(key, config): from_untyped_object(value, config)
        for key, value in dct.items()
    }


def from_untyped_object(obj: Any, config: SerializerConfig) -> Any:
    if isinstance(obj, dict):
        return _from_dict(obj, config)
    elif isinstance(obj, list):
        return _from_list(obj, config)
    else:
        return _from_value(obj, type(obj), config)


def serialize_untyped(
        obj: Any,
        config: SerializerConfig | None = None,
        encode: JSONEncoder | None = None
) -> str:
    json_obj = from_untyped_object(obj, config or DEFAULT_CONFIG)
    return (encode or ENCODE_JSON)(json_obj)
