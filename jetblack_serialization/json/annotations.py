"""XML annotations"""

from typing import Tuple, cast

from ..types import Annotation
from ..custom_annotations import (
    SerializationAnnotation,
    is_any_serialization_annotation,
    get_all_serialization_annotations
)


class JSONAnnotation(SerializationAnnotation):
    """The base JSON annotation class"""


class JSONValue(JSONAnnotation):
    """A JSON property"""

    def __repr__(self) -> str:
        return 'JSONValue()'


class JSONProperty(JSONAnnotation):
    """A JSON property"""

    def __init__(self, tag: str):
        self.tag = tag

    def __repr__(self) -> str:
        return f'JSONProperty(tag="{self.tag}")'


def is_json_annotation(annotation: Annotation) -> bool:
    """Determine if the annotation is of type Annotation[T, JSONAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        bool: True if the annotation is of type Annotation[T, JSONAnnotation],
            otherwise False
    """
    if not is_any_serialization_annotation(annotation):
        return False
    _, serialization_annotations = get_all_serialization_annotations(
        annotation
    )
    json_annotations = [
        serialization_annotation
        for serialization_annotation in serialization_annotations
        if issubclass(type(serialization_annotation), JSONAnnotation)
    ]
    return len(json_annotations) == 1


def get_json_annotation(annotation: Annotation) -> Tuple[Annotation, JSONAnnotation]:
    """Gets the type T of Annotation[T, JSONAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        Tuple[Annotation, JSONAnnotation]: The type and the JSON annotation
    """
    type_annotation, serialization_annotations = get_all_serialization_annotations(
        annotation
    )
    json_annotations = [
        serialization_annotation
        for serialization_annotation in serialization_annotations
        if issubclass(type(serialization_annotation), JSONAnnotation)
    ]
    return type_annotation, cast(JSONAnnotation, json_annotations[0])
