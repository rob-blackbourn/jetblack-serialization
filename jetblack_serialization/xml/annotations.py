"""XML annotations"""

from typing import Tuple, cast

from ..types import Annotation
from ..custom_annotations import (
    SerializationAnnotation,
    is_any_serialization_annotation,
    get_all_serialization_annotations
)


class XMLAnnotation(SerializationAnnotation):
    """The base XML annotation class"""

    def __init__(self, tag: str):
        self.tag = tag


class XMLEntity(XMLAnnotation):
    """An XML entity"""

    def __repr__(self) -> str:
        return f'XMLEntity("tag={self.tag}")'


class XMLAttribute(XMLAnnotation):
    """An XML attribute"""

    def __repr__(self) -> str:
        return f'XMLAttribute(tag="{self.tag}")'

DEFAULT_DOCUMENT_ANNOTATION = XMLEntity('document')
DEFAULT_KEY_ANNOTATION = XMLEntity('key')
DEFAULT_VALUE_ANNOTATION = XMLEntity('value')


def is_xml_annotation(annotation: Annotation) -> bool:
    """Determine if the annotation is of type Annotation[T, XMLAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        bool: True if the annotation is of type Annotation[T, XMLAnnotation],
            otherwise False
    """
    if not is_any_serialization_annotation(annotation):
        return False
    _, serialization_annotations = get_all_serialization_annotations(
        annotation
    )
    xml_annotations = [
        serialization_annotation
        for serialization_annotation in serialization_annotations
        if issubclass(type(serialization_annotation), XMLAnnotation)
    ]
    return len(xml_annotations) == 1


def get_xml_annotation(
        annotation: Annotation,
        default: XMLAnnotation
) -> Tuple[Annotation, XMLAnnotation]:
    """Gets the type T of Annotation[T, XMLAnnotation]

    Args:
        annotation (Any): The annotation
        default (XMLAnnotation): The default annotation.

    Returns:
        Tuple[Annotation, XMLAnnotation]: The type and the XML annotation
    """
    type_annotation, serialization_annotations = get_all_serialization_annotations(
        annotation
    )
    xml_annotations = [
        serialization_annotation
        for serialization_annotation in serialization_annotations
        if issubclass(type(serialization_annotation), XMLAnnotation)
    ]
    xml_annotation = xml_annotations[0] if xml_annotations else default
    return type_annotation, cast(XMLAnnotation, xml_annotation)
