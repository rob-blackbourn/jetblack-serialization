"""JSON annotations"""

from typing import Any, Callable, cast

from ..types import Annotation
from ..custom_annotations import (
    SerializationAnnotation,
    is_any_serialization_annotation,
    get_all_serialization_annotations
)

type TypeSelector = Callable[[Any, Annotation], Annotation]


class JSONAnnotation(SerializationAnnotation):
    """The base JSON annotation class"""

    def __init__(
            self,
            type_selector: TypeSelector | None = None
    ) -> None:
        self.type_selector = type_selector


class JSONValue(JSONAnnotation):
    """A JSON property"""

    def __repr__(self) -> str:
        return 'JSONValue()'


class JSONProperty(JSONAnnotation):
    """A JSON property"""

    def __init__(
            self,
            tag: str,
            type_selector: TypeSelector | None = None
    ) -> None:
        super().__init__(type_selector)
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


def get_json_annotation(annotation: Annotation) -> tuple[Annotation, JSONAnnotation]:
    """Gets the type T of Annotation[T, JSONAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        tuple[Annotation, JSONAnnotation]: The type and the JSON annotation
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
