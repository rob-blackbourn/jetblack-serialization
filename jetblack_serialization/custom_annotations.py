"""Custom annotations"""

from abc import ABCMeta
from typing import Any, List, Tuple

import jetblack_serialization.typing_inspect_ex as typing_inspect
from .types import Annotation


class SerializationAnnotation(metaclass=ABCMeta):
    """The base serialization annotation class"""

class DefaultAnnotation:

    def __init__(self, value: Any) -> None:
        self.value = value

def is_any_serialization_annotation(annotation: Annotation) -> bool:
    """Determine if the annotation is of type Annotation[T, SerializationAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        bool: True if the annotation is of type
            Annotation[T, SerializationAnnotation], otherwise False
    """
    if not typing_inspect.is_annotated_type(annotation):
        return False
    for item in typing_inspect.get_metadata(annotation):
        if issubclass(type(item), SerializationAnnotation):
            return True
    return False


def get_all_serialization_annotations(
        annotation: Annotation
) -> Tuple[Annotation, List[SerializationAnnotation]]:
    """Gets the type T of Annotation[T, SerializationAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        Tuple[Annotation, List[SerializationAnnotation]]: The type and the
            serialization annotationa
    """
    type_annotation = typing_inspect.get_origin(annotation)
    serialization_annotations = [
        serialization_annotation
        for serialization_annotation in typing_inspect.get_metadata(annotation)
        if issubclass(type(serialization_annotation), SerializationAnnotation)
    ]
    return type_annotation, serialization_annotations
