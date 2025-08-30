"""Custom annotations"""

from abc import ABCMeta
from inspect import Signature
from typing import Any, Callable

from .types import Annotation
from .typing_ex import is_annotated, get_annotated_type, get_metadata


class SerializationAnnotation(metaclass=ABCMeta):
    """The base serialization annotation class"""


class DefaultValue:

    def __init__(self, value: Any) -> None:
        self.value = value


class DefaultFactory[T]:

    def __init__(self, factory: Callable[[], T]) -> None:
        self.factory = factory


def is_any_annotation_of_type(annotation: Annotation, tp: type[Any]) -> bool:
    if not is_annotated(annotation):
        return False
    for item in get_metadata(annotation) or []:
        if issubclass(type(item), tp):
            return True
    return False


def get_all_annotations_of_type[T](
        annotation: Annotation,
        tp: type[T]
) -> tuple[Annotation, list[T]]:
    type_annotation = get_annotated_type(annotation)
    serialization_annotations = [
        serialization_annotation
        for serialization_annotation in get_metadata(annotation) or []
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
) -> tuple[Annotation, list[SerializationAnnotation]]:
    """Gets the type T of Annotation[T, SerializationAnnotation]

    Args:
        annotation (Any): The annotation

    Returns:
        tuple[Annotation, list[SerializationAnnotation]]: The type and the
            serialization annotation
    """
    return get_all_annotations_of_type(annotation, SerializationAnnotation)


def is_any_default_annotation(annotation: Annotation) -> bool:
    return is_any_annotation_of_type(annotation, DefaultValue)


def is_any_default_factory_annotation(annotation: Annotation) -> bool:
    return is_any_annotation_of_type(annotation, DefaultFactory)


def get_annotation_of_type[T](
        annotation: Annotation,
        annotation_type: type[T]
) -> tuple[Annotation, T]:
    typ, annotations = get_all_annotations_of_type(annotation, annotation_type)
    assert len(annotations) == 1, "There can be only one"
    return typ, annotations[0]


def get_default_annotation(
        annotation: Annotation
) -> tuple[Annotation, DefaultValue]:
    return get_annotation_of_type(annotation, DefaultValue)


def get_default_factory_annotation(
        annotation: Annotation
) -> tuple[Annotation, DefaultFactory]:
    return get_annotation_of_type(annotation, DefaultFactory)


def get_typed_dict_key_default(td) -> Any:
    if is_any_default_annotation(td):
        _, default = get_default_annotation(td)
        return default.value
    elif is_any_default_factory_annotation(td):
        _, annotation = get_default_factory_annotation(td)
        return annotation.factory()
    return Signature.empty
