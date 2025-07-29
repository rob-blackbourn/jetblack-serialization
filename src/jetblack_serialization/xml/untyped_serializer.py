"""Untyped XML serialization"""

from decimal import Decimal
from typing import Any

from lxml.etree import Element, _Element, SubElement  # pylint: disable=no-name-in-module

from ..config import SerializerConfig, DEFAULT_CONFIG

from .encoding import XMLEncoder, ENCODE_XML


def _make_object(parent: _Element | None, type_name: str) -> _Element:
    element = Element('object') if parent is None else SubElement(
        parent, 'object')
    element.set('type', type_name)
    return element


def _from_value(
        value: Any,
        config: SerializerConfig
) -> str:
    if isinstance(value, str):
        return value
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    elif isinstance(value, float):
        return str(value)
    elif isinstance(value, Decimal):
        return str(value)
    else:
        serializer = config.value_serializers.get(type(value))
        if serializer is not None:
            return serializer(value)

    raise TypeError(f'Unhandled type {type(value)}')


def _from_list(
        obj: list,
        parent: _Element | None,
        config: SerializerConfig
) -> _Element:
    element = _make_object(parent, 'list')

    for item in obj:
        _from_obj(
            item,
            element,
            config
        )

    return element


def _from_dict(
        obj: dict,
        parent: _Element | None,
        config: SerializerConfig
) -> _Element:
    element = _make_object(parent, 'dict')

    for key, value in obj.items():
        item_element = _make_object(element, 'dict-entry')
        _from_obj(
            key,
            item_element,
            config
        ).set('role', 'key')
        _from_obj(
            value,
            item_element,
            config
        ).set('role', 'value')

    return element


def _from_simple(
        obj: Any,
        parent: _Element | None,
        config: SerializerConfig
) -> _Element:
    text = _from_value(obj, config)
    child = _make_object(parent, obj.__class__.__name__)
    child.text = text
    return child


def _from_obj(
        obj: Any,
        element: _Element | None,
        config: SerializerConfig
) -> _Element:
    if isinstance(obj, dict):
        return _from_dict(obj, element, config)
    elif isinstance(obj, list):
        return _from_list(obj, element, config)
    else:
        return _from_simple(obj, element, config)


def serialize_untyped(
        obj: Any,
        config: SerializerConfig | None = None,
        encode: XMLEncoder | None = None
) -> str:
    element = _from_obj(obj, None, config or DEFAULT_CONFIG)
    return (encode or ENCODE_XML)(element)
