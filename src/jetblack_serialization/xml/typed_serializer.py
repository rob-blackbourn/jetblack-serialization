"""Typed XML serialization"""

from decimal import Decimal
from enum import Enum
from inspect import Parameter
from typing import Any, Union, get_args, is_typeddict

from lxml.etree import Element, _Element, SubElement  # pylint: disable=no-name-in-module

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..types import Annotation
from ..typing_ex import (
    is_annotated,
    is_list,
    is_optional,
    is_union,
    typeddict_keys
)
from ..utils import is_value_type

from .annotations import (
    XMLAnnotation,
    XMLAttribute,
    XMLEntity,
    get_xml_annotation
)
from .encoding import XMLEncoder, ENCODE_XML


def _make_element(parent: _Element | None, tag: str) -> _Element:
    return Element(tag) if parent is None else SubElement(parent, tag)


def _from_value(
        value: Any,
        type_annotation: type,
        config: SerializerConfig
) -> str:
    if type_annotation is str:
        return value
    elif type_annotation is int:
        return str(value)
    elif type_annotation is bool:
        return 'true' if value else 'false'
    elif type_annotation is float:
        return str(value)
    elif type_annotation is Decimal:
        return str(value)
    elif isinstance(value, Enum):
        return value.name
    else:
        serializer = config.value_serializers.get(type_annotation)
        if serializer is not None:
            return serializer(value)

    raise TypeError(f'Unhandled type {type_annotation}')


def _from_optional(
        obj: Any,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        element: _Element | None,
        config: SerializerConfig
) -> _Element:
    if obj is None:
        return _make_element(element, xml_annotation.tag)

    # An optional is a union where the last element is the None type.
    union_types = get_args(type_annotation)[:-1]
    if len(union_types) == 1:
        # This was Optional[T]
        return _from_obj(
            obj,
            union_types[0],
            xml_annotation,
            element,
            config
        )
    else:
        return _from_union(
            obj,
            Union[tuple(union_types)],  # type: ignore
            xml_annotation,
            element,
            config
        )


def _from_union(
        obj: Any,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        element: _Element | None,
        config: SerializerConfig
) -> _Element:
    for union_type_annotation in get_args(type_annotation):
        try:
            return _from_obj(
                obj,
                union_type_annotation,
                xml_annotation,
                element,
                config
            )
        except:  # pylint: disable=bare-except
            pass

    raise ValueError('unable to find type that satisfies union')


def _from_list(
        obj: list,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        element: _Element | None,
        config: SerializerConfig
) -> _Element:
    item_annotation, *_rest = get_args(type_annotation)
    if is_annotated(item_annotation):
        item_type_annotation, item_xml_annotation = get_xml_annotation(
            item_annotation
        )
    else:
        item_type_annotation = item_annotation
        item_xml_annotation = xml_annotation

    if element is None:
        element = Element(xml_annotation.tag)

    if xml_annotation.tag == item_xml_annotation.tag:
        # siblings
        parent = element
    else:
        parent = _make_element(element, xml_annotation.tag)

    for item in obj:
        _from_obj(
            item,
            item_type_annotation,
            item_xml_annotation,
            parent,
            config
        )

    return parent


def _from_typed_dict(
        obj: dict,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        element: _Element | None,
        config: SerializerConfig
) -> _Element:
    dict_element = _make_element(element, xml_annotation.tag)

    typed_dict_keys = typeddict_keys(type_annotation)
    assert typed_dict_keys is not None
    for key, info in typed_dict_keys.items():
        default = getattr(type_annotation, key, Parameter.empty)
        if is_annotated(info.annotation):
            item_type_annotation, item_xml_annotation = get_xml_annotation(
                info.annotation
            )
        else:
            tag = config.serialize_key(key) if isinstance(key, str) else key
            item_type_annotation = info.annotation
            item_xml_annotation = XMLEntity(tag)

        value = obj.get(key, default)
        if value is not Parameter.empty:
            _from_obj(
                value,
                item_type_annotation,
                item_xml_annotation,
                dict_element,
                config
            )
        else:
            # TODO: Should we throw?
            pass

    return dict_element


def _from_simple(
        obj: Any,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        element: _Element | None,
        config: SerializerConfig
) -> _Element:
    text = _from_value(obj, type_annotation, config)
    if isinstance(xml_annotation, XMLAttribute):
        if element is None:
            raise ValueError("No element for attribute")
        element.set(xml_annotation.tag, text)
        return element
    else:
        child = _make_element(element, xml_annotation.tag)
        child.text = text
        return child


def _from_obj(
        obj: Any,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        element: _Element | None,
        config: SerializerConfig
) -> _Element:
    if is_value_type(type_annotation, config.value_serializers.keys()):
        return _from_simple(
            obj,
            type_annotation,
            xml_annotation,
            element,
            config
        )
    elif is_optional(type_annotation):
        return _from_optional(
            obj,
            type_annotation,
            xml_annotation,
            element,
            config
        )
    elif is_list(type_annotation):
        return _from_list(
            obj,
            type_annotation,
            xml_annotation,
            element,
            config
        )
    elif is_typeddict(type_annotation):
        return _from_typed_dict(
            obj,
            type_annotation,
            xml_annotation,
            element,
            config
        )
    elif is_union(type_annotation):
        return _from_union(
            obj,
            type_annotation,
            xml_annotation,
            element,
            config
        )
    else:
        raise TypeError


def serialize_typed(
        obj: Any,
        annotation: Annotation,
        config: SerializerConfig | None = None,
        encode: XMLEncoder | None = None
) -> str:
    type_annotation, xml_annotation = get_xml_annotation(annotation)
    if not isinstance(xml_annotation, XMLEntity):
        raise TypeError(
            "Expected the root value to have an XMLEntity annotation")

    element = _from_obj(
        obj,
        type_annotation,
        xml_annotation,
        None,
        config or DEFAULT_CONFIG
    )
    return (encode or ENCODE_XML)(element)
