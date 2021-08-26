"""XML Serialization"""

from decimal import Decimal
from inspect import Parameter
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Type,
    Union
)

from lxml import etree
from lxml.etree import _Element  # pylint: disable=no-name-in-module

from .. import typing_inspect_ex as typing_inspect
from ..config import SerializerConfig
from ..custom_annotations import get_typed_dict_key_default
from ..types import Annotation
from ..utils import is_simple_type

from .annotations import (
    XMLAnnotation,
    XMLAttribute,
    XMLEntity,
    get_xml_annotation
)


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
        text: Optional[str],
        default: Any,
        type_annotation: Type,
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
    else:
        deserializer = config.value_deserializers.get(type_annotation)
        if deserializer is not None:
            return deserializer(text)

    raise TypeError(f'Unhandled type {type_annotation}')


def _to_union(
        element: Optional[_Element],
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> Any:
    for union_type_annotation in typing_inspect.get_args(type_annotation):
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
        element: Optional[_Element],
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> Any:
    if element is None or _is_element_empty(element, xml_annotation):
        return None

    # An optional is a union where the last element is the None type.
    union_types = typing_inspect.get_args(type_annotation)[:-1]
    if len(union_types) == 1:
        # This was Optional[T]
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
            Union[tuple(union_types)],
            xml_annotation,
            config
        )


def _to_simple(
        element: Optional[_Element],
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
        text = element.attrib[xml_annotation.tag]
    if text is None and default is Parameter.empty:
        raise ValueError(f'Expected "{xml_annotation.tag}" to be non-null')
    if isinstance(text, bytes):
        text = text.decode()
    return _to_value(text, default, type_annotation, config)


def _to_list(
        element: Optional[_Element],
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> List[Any]:
    if element is None:
        raise ValueError('Received "None" while deserializing a list')

    item_annotation, *_rest = typing_inspect.get_args(type_annotation)
    if typing_inspect.is_annotated_type(item_annotation):
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
        element: Optional[_Element],
        type_annotation: Annotation,
        config: SerializerConfig
) -> Optional[Dict[str, Any]]:
    if element is None:
        raise ValueError('Received "None" while deserializing a TypeDict')

    typed_dict: Dict[str, Any] = {}

    typed_dict_keys = typing_inspect.typed_dict_keys(type_annotation)
    for key, key_annotation in typed_dict_keys.items():
        default = get_typed_dict_key_default(key_annotation)
        if typing_inspect.is_annotated_type(key_annotation):
            item_type_annotation, item_xml_annotation = get_xml_annotation(
                key_annotation
            )
        else:
            tag = config.serialize_key(key) if isinstance(key, str) else key
            item_xml_annotation = XMLEntity(tag)
            item_type_annotation = typing_inspect.get_unannotated_type(
                key_annotation
            )

        if not isinstance(item_xml_annotation, XMLAttribute):
            item_element = element.find('./' + item_xml_annotation.tag)
        else:
            item_element = element

        typed_dict[key] = _to_obj(
            item_element,
            default,
            item_type_annotation,
            item_xml_annotation,
            config
        )

    return typed_dict


def _to_obj(
        element: Optional[_Element],
        default: Optional[Any],
        type_annotation: Annotation,
        xml_annotation: XMLAnnotation,
        config: SerializerConfig
) -> Any:

    if is_simple_type(type_annotation):
        return _to_simple(
            element,
            default,
            type_annotation,
            xml_annotation,
            config
        )
    if typing_inspect.is_optional_type(type_annotation):
        return _to_optional(
            element,
            type_annotation,
            xml_annotation,
            config
        )
    elif typing_inspect.is_list_type(type_annotation):
        return _to_list(
            element,
            type_annotation,
            xml_annotation,
            config
        )
    elif typing_inspect.is_typed_dict_type(type_annotation):
        return _to_typed_dict(
            element,
            type_annotation,
            config)
    elif typing_inspect.is_union_type(type_annotation):
        return _to_union(
            element,
            type_annotation,
            xml_annotation,
            config
        )
    raise TypeError


def deserialize(
        text: str,
        annotation: Annotation,
        config: SerializerConfig
) -> Any:
    """Convert XML to an object

    Args:
        text (str): The XML string
        annotation (str): The type annotation

    Returns:
        Any: The deserialized object.
    """
    type_annotation, xml_annotation = get_xml_annotation(annotation)
    if not isinstance(xml_annotation, XMLEntity):
        raise TypeError(
            "Expected the root value to have an XMLEntity annotation")

    element = etree.fromstring(text)  # pylint: disable=c-extension-no-member
    return _to_obj(element, Parameter.empty, type_annotation, xml_annotation, config)
