"""An untyped serializer"""

from datetime import datetime, timedelta
import json
from typing import Any

from ..iso_8601 import datetime_to_iso_8601, timedelta_to_iso_8601
from ..config import SerializerConfig


def _serialize_key_if_str(key: Any, config: SerializerConfig) -> Any:
    return config.serialize_key(
        key
    ) if config.serialize_key and isinstance(key, str) else key


def _from_value(value: Any) -> Any:
    if isinstance(value, timedelta):
        return timedelta_to_iso_8601(value)
    elif isinstance(value, datetime):
        return datetime_to_iso_8601(value)
    else:
        return value


def _from_list(lst: list, config: SerializerConfig) -> list:
    return [
        _from_obj(item, config)
        for item in lst
    ]


def _from_dict(dct: dict, config: SerializerConfig) -> dict:
    return {
        _serialize_key_if_str(key, config): _from_obj(value, config)
        for key, value in dct.items()
    }


def _from_obj(obj: Any, config: SerializerConfig) -> Any:
    if isinstance(obj, dict):
        return _from_dict(obj, config)
    elif isinstance(obj, list):
        return _from_list(obj, config)
    else:
        return _from_value(obj)


def serialize(obj: Any, config: SerializerConfig) -> str:
    json_obj = _from_obj(obj, config)
    return json.dumps(json_obj)
