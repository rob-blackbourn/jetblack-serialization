"""Untyped XML deserialization"""

from decimal import Decimal
from typing import Any

from lxml.etree import _Element  # pylint: disable=no-name-in-module

from ..config import SerializerConfig, DEFAULT_CONFIG

from .encoding import XMLDecoder, DECODE_XML


def _is_element_empty(element: _Element) -> bool:  # TODO: Remove this?
    return (
        element.find('*') is None and
        element.text is None and
        not element.attrib
    )


def _to_value(
        text: str | None,
        type_name: str,
        config: SerializerConfig
) -> Any:
    if text is None:
        return None
    elif type_name == str.__name__:
        return text
    elif type_name == int.__name__:
        return int(text)
    elif type_name == bool.__name__:
        return text.lower() == 'true'
    elif type_name == float.__name__:
        return float(text)
    elif type_name == Decimal.__name__:
        return Decimal(text)
    else:
        for cls, deserializer in config.value_deserializers.items():
            if type_name == cls.__name__:
                return deserializer(text)

    raise TypeError(f'Unhandled type {type_name}')


def _to_simple(
        element: _Element | None,
        config: SerializerConfig
) -> Any:
    if element is None:
        raise ValueError('Found "None" while deserializing a value')

    text = element.text
    if isinstance(text, memoryview):
        text = text.tobytes().decode()
    elif isinstance(text, (bytes, bytearray)):
        text = text.decode()

    type_name = element.get('type')
    if type_name is None:
        raise ValueError('The type attribute is missing')
    if isinstance(type_name, bytes):
        type_name = type_name.decode()

    return _to_value(text, type_name, config)


def _to_list(
        parent: _Element | None,
        config: SerializerConfig
) -> list[Any]:
    if parent is None:
        raise ValueError('Received "None" while deserializing a list')

    return [
        _to_obj(
            element,
            config
        )
        for element in parent.iterchildren()
    ]


def _to_dict(
        element: _Element | None,
        config: SerializerConfig
) -> dict[str, Any] | None:
    if element is None:
        raise ValueError('Received "None" while deserializing a TypeDict')

    return {
        _to_obj(
            entry.find('./object[@role="key"]'),
            config
        ): _to_obj(
            entry.find('./object[@role="value"]'),
            config
        )
        for entry in element.iterchildren()
    }


def _to_obj(
        element: _Element | None,
        config: SerializerConfig
) -> Any:

    if element is None:
        return None
    elif element.get('type') == 'dict':
        return _to_dict(element, config)
    elif element.get('type') == 'list':
        return _to_list(element, config)
    else:
        return _to_simple(element, config)


def deserialize_untyped(
        text: str | bytes | bytearray,
        config: SerializerConfig | None = None,
        decode: XMLDecoder | None = None
) -> Any:
    """Deserialize XML without type information

    Args:
        text (str | bytes | bytearray): The XML string

    Returns:
        Any: The deserialized object.
    """
    element = (decode or DECODE_XML)(text)
    return _to_obj(element, config or DEFAULT_CONFIG)
