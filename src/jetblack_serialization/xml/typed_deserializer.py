"""Typed XML deserialization"""

from decimal import Decimal
from enum import Enum
from inspect import Parameter, isclass
from typing import Any, Iterable, Union, get_args, is_typeddict

from lxml.etree import _Element  # pylint: disable=no-name-in-module

from ..config import SerializerConfig, DEFAULT_CONFIG
from ..custom_annotations import get_typed_dict_key_default
from ..types import Annotation
from ..typing_ex import (
    is_annotated,
    is_list,
    is_optional,
    is_union,
    get_unannotated,
    typeddict_keys
)
from ..utils import is_value_type

from .annotations import (
    XMLAnnotation,
    XMLAttribute,
    XMLEntity,
    get_xml_annotation
)
from .encoding import XMLDecoder, DECODE_XML


def _is_element_empty(element: _Element, xml_annotation: XMLAnnotation) -> bool:
    if isinstance(xml_annotation, XMLAttribute):
        return xml_annotation.tag not in element.attrib
    else:
        return (
            element.find('*') is None and
            element.text is None and
            not element.attrib
        )


def _to_value(
        text: str | None,
        default: Any,
        type_annotation: type,
        config: SerializerConfig
) -> Any:
    if text is None:
        return default
    elif type_annotation is str:
        return text
    elif type_annotation is int:
        return int(text)
    elif type_annotation is bool:
        return text.lower() == 'true'
    elif type_annotation is float:
        return float(text)
    elif type_annotation is Decimal:
        return Decimal(text)
    elif isclass(type_annotation) and issubclass(type_annotation, Enum):
        return type_annotation[text]
    else:
        deserializer = config.value_deserializers.get(type_annotation)
        if deserializer is not None:
            return deserializer(text)

    raise TypeError(f'Unhandled type {type_annotation}')


def _to_union(
        element: _Element | None,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> Any:
    for union_type_annotation in get_args(type_annotation):
        try:
            return _to_obj(
                element,
                Parameter.empty,
                union_type_annotation,
                xml_annotation,
                config
            )
        except:  # pylint: disable=bare-except
            pass
    raise ValueError('Unable to deserialize a Union')


def _to_optional(
        element: _Element | None,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> Any:
    if element is None or _is_element_empty(element, xml_annotation):
        return None

    # An optional is a union where the last element is the None type.
    # TODO: review this.
    union_types = get_args(type_annotation)[:-1]
    if len(union_types) == 1:
        # This was T | None
        return _to_obj(
            element,
            Parameter.empty,
            union_types[0],
            xml_annotation,
            config
        )
    else:
        return _to_union(
            element,
            Union[tuple(union_types)],  # type: ignore
            xml_annotation,
            config
        )


def _to_simple(
        element: _Element | None,
        default: Any,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> Any:
    if element is None:
        raise ValueError('Found "None" while deserializing a value')
    if not isinstance(xml_annotation, XMLAttribute):
        text = element.text
    else:
        attrib = element.attrib[xml_annotation.tag]
        text = attrib.decode('utf8') if isinstance(attrib, bytes) else attrib
    if text is None and default is Parameter.empty:
        raise ValueError(f'Expected "{xml_annotation.tag}" to be non-null')
    if isinstance(text, bytes):
        text = text.decode()
    assert isinstance(text, str)
    return _to_value(text, default, type_annotation, config)


def _to_list(
        element: _Element | None,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> list[Any]:
    if element is None:
        raise ValueError('Received "None" while deserializing a list')

    item_annotation, *_rest = get_args(type_annotation)
    if is_annotated(item_annotation):
        item_type_annotation, item_xml_annotation = get_xml_annotation(
            item_annotation
        )
    else:
        item_type_annotation = item_annotation
        item_xml_annotation = xml_annotation

    if xml_annotation.tag == item_xml_annotation.tag:
        # siblings
        elements: Iterable[_Element] = element.iterfind(
            '../' + item_xml_annotation.tag)
    else:
        # nested
        elements = element.iter(item_xml_annotation.tag)

    return [
        _to_obj(
            child,
            Parameter.empty,
            item_type_annotation,
            item_xml_annotation,
            config
        )
        for child in elements
    ]


def _to_typed_dict(
        element: _Element | None,
        type_annotation: Annotation,
        config: SerializerConfig
) -> dict[str, Any] | None:
    if element is None:
        raise ValueError('Received "None" while deserializing a TypeDict')

    typed_dict: dict[str, Any] = {}

    typed_dict_keys = typeddict_keys(type_annotation)
    assert typed_dict_keys is not None
    for key, info in typed_dict_keys.items():
        default = get_typed_dict_key_default(info.annotation)
        if is_annotated(info.annotation):
            item_type_annotation, item_xml_annotation = get_xml_annotation(
                info.annotation
            )
        else:
            tag = config.serialize_key(key) if isinstance(key, str) else key
            item_xml_annotation = XMLEntity(tag)
            item_type_annotation = get_unannotated(info.annotation)

        if (
                isinstance(item_xml_annotation, XMLAttribute) or
                item_xml_annotation.tag == ''
        ):
            item_element: _Element | None = element
        else:
            item_element = element.find('./' + item_xml_annotation.tag)

        typed_dict[key] = _to_obj(
            item_element,
            default,
            item_type_annotation,
            item_xml_annotation,
            config
        )

    return typed_dict


def _to_obj(
        element: _Element | None,
        default: Any | None,
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> Any:

    if is_value_type(type_annotation, config.value_deserializers.keys()):
        return _to_simple(
            element,
            default,
            type_annotation,
            xml_annotation,
            config
        )
    if is_optional(type_annotation):
        return _to_optional(
            element,
            type_annotation,
            xml_annotation,
            config
        )
    elif is_list(type_annotation):
        return _to_list(
            element,
            type_annotation,
            xml_annotation,
            config
        )
    elif is_typeddict(type_annotation):
        return _to_typed_dict(
            element,
            type_annotation,
            config)
    elif is_union(type_annotation):
        return _to_union(
            element,
            type_annotation,
            xml_annotation,
            config
        )
    raise TypeError


def deserialize_typed(
        text: str | bytes | bytearray,
        annotation: Annotation,
        config: SerializerConfig | None = None,
        decode: XMLDecoder | None = None
) -> Any:
    """Convert XML to an object

    Args:
        text (str | bytes | bytearray): The XML string
        annotation (str): The type annotation

    Returns:
        Any: The deserialized object.
    """
    type_annotation, xml_annotation = get_xml_annotation(annotation)
    if not isinstance(xml_annotation, XMLEntity):
        raise TypeError(
            "Expected the root value to have an XMLEntity annotation"
        )

    element = (decode or DECODE_XML)(text)
    return _to_obj(
        element,
        Parameter.empty,
        type_annotation,
        xml_annotation,
        config or DEFAULT_CONFIG
    )
