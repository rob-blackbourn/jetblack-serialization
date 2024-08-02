"""Untyped JSON deserialization"""

import json
from typing import Any, Union

from ..config import BaseSerializerConfig

from .config import SerializerConfig


def _deserialize_key_if_str(key: Any, config: BaseSerializerConfig) -> Any:
    return config.deserialize_key(
        key
    ) if config.deserialize_key is not None and isinstance(key, str) else key


def _from_value(
        value: Any,
        config: BaseSerializerConfig
) -> Any:
    if isinstance(value, str):
        for deserializer in config.value_deserializers.values():
            try:
                return deserializer(value)
            except:  # pylint: disable=bare-except
                pass
    return value


def _from_list(lst: list, config: BaseSerializerConfig) -> list:
    return [
        from_untyped_object(item, config)
        for item in lst
    ]


def _from_dict(dct: dict, config: BaseSerializerConfig) -> dict:
    return {
        _deserialize_key_if_str(key, config): from_untyped_object(value, config)
        for key, value in dct.items()
    }


def from_untyped_object(obj: Any, config: BaseSerializerConfig) -> Any:
    if isinstance(obj, dict):
        return _from_dict(obj, config)
    elif isinstance(obj, list):
        return _from_list(obj, config)
    else:
        return _from_value(obj, config)


def deserialize_untyped(
        text: Union[str, bytes, bytearray],
        config: SerializerConfig
) -> Any:
    """Deserialize JSON without type information

    Args:
        text (Union[str, bytes, bytearray]): The JSON string

    Returns:
        Any: The deserialized JSON object
    """

    def _hook(obj: dict) -> dict:
        return _from_dict(obj, config)

    return json.loads(text, object_hook=_hook)
