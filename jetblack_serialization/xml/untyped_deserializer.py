"""XML Serialization"""

from decimal import Decimal
from typing import Any, AnyStr, Dict, List, Optional, cast

from lxml import etree
from lxml.etree import _Element  # pylint: disable=no-name-in-module

from ..config import SerializerConfig


def _is_element_empty(element: _Element) -> bool:
    return (
        element.find('*') is None and
        element.text is None and
        not element.attrib
    )


def _to_value(
        text: Optional[str],
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
        element: Optional[_Element],
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
        parent: Optional[_Element],
        config: SerializerConfig
) -> List[Any]:
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
        element: Optional[_Element],
        config: SerializerConfig
) -> Optional[Dict[str, Any]]:
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
        element: Optional[_Element],
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


def deserialize_untyped(text: AnyStr, config: SerializerConfig) -> Any:
    """Deserialize XML without type information

    Args:
        text (AnyStr): The XML string

    Returns:
        Any: The deserialized object.
    """
    element = etree.fromstring(text)  # pylint: disable=c-extension-no-member
    return _to_obj(element, config)
