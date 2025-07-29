"""Untyped JSON deserialization"""

from typing import Any

from ..config import SerializerConfig, DEFAULT_CONFIG

from .encoding import JSONDecoder, DECODE_JSON


def _deserialize_key_if_str(key: Any, config: SerializerConfig) -> Any:
    return config.deserialize_key(
        key
    ) if config.deserialize_key is not None and isinstance(key, str) else key


def _from_value(
        value: Any,
        config: SerializerConfig
) -> Any:
    if isinstance(value, str):
        for deserializer in config.value_deserializers.values():
            try:
                return deserializer(value)
            except:  # pylint: disable=bare-except
                pass
    return value


def _from_list(lst: list, config: SerializerConfig) -> list:
    return [
        from_untyped_object(item, config)
        for item in lst
    ]


def _from_dict(dct: dict, config: SerializerConfig) -> dict:
    return {
        _deserialize_key_if_str(key, config): from_untyped_object(value, config)
        for key, value in dct.items()
    }


def from_untyped_object(obj: Any, config: SerializerConfig) -> Any:
    if isinstance(obj, dict):
        return _from_dict(obj, config)
    elif isinstance(obj, list):
        return _from_list(obj, config)
    else:
        return _from_value(obj, config)


def deserialize_untyped(
        text: str | bytes | bytearray,
        config: SerializerConfig | None = None,
        decode: JSONDecoder | None = None
) -> Any:
    """Deserialize JSON without type information

    Args:
        text (str | bytes | bytearray): The JSON string

    Returns:
        Any: The deserialized JSON object
    """
    json_obj = (decode or DECODE_JSON)(text)
    return from_untyped_object(json_obj, config or DEFAULT_CONFIG)
