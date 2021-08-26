"""Custom annotations"""

from abc import ABCMeta
from inspect import Signature
from typing import Any, List, Tuple, Type, TypeVar

import jetblack_serialization.typing_inspect_ex as typing_inspect
from .types import Annotation

T = TypeVar('T')


class SerializationAnnotation(metaclass=ABCMeta):
    """The base serialization annotation class"""


class DefaultValue:

    def __init__(self, value: Any) -> None:
        self.value = value


def is_any_annotation_of_type(annotation: Annotation, tp: Type[Any]) -> bool:
    if not typing_inspect.is_annotated_type(annotation):
        return False
    for item in typing_inspect.get_metadata(annotation):
        if issubclass(type(item), tp):
            return True
    return False


def get_all_annotations_of_type(
        annotation: Annotation,
        tp: Type[T]
) -> Tuple[Annotation, List[T]]:
    type_annotation = typing_inspect.get_origin(annotation)
    serialization_annotations = [
        serialization_annotation
        for serialization_annotation in typing_inspect.get_metadata(annotation)
        if issubclass(type(serialization_annotation), tp)
    ]
    return type_annotation, serialization_annotations


def is_any_serialization_annotation(annotation: Annotation) -> bool:
    """Determine if the annotation is of type Annotation[T, SerializationAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        bool: True if the annotation is of type
            Annotation[T, SerializationAnnotation], otherwise False
    """
    return is_any_annotation_of_type(annotation, SerializationAnnotation)


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
    return get_all_annotations_of_type(annotation, SerializationAnnotation)


def is_any_default_annotation(annotation: Annotation) -> bool:
    return is_any_annotation_of_type(annotation, DefaultValue)


def get_default_annotation(
        annotation: Annotation
) -> Tuple[Annotation, DefaultValue]:
    typ, annotations = get_all_annotations_of_type(
        annotation, DefaultValue)
    assert len(annotations) == 1, "There can be only one"
    return typ, annotations[0]


def get_typed_dict_key_default(td):
    if is_any_default_annotation(td):
        _, annotation = get_default_annotation(td)
        return annotation.value
    return Signature.empty
