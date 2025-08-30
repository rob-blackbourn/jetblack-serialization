"""Protocol utilities"""

from enum import Enum
from inspect import isclass
from typing import Any, Iterable, Sequence, get_args, is_typeddict

from .types import Annotation
from .typing_ex import (
    get_annotated_type,
    get_optional_types,
    is_annotated,
    is_dict,
    is_list,
    is_optional,
)

BUILTIN_TYPES: Sequence[type] = (
    str,
    bool,
    int,
    float
)


def is_value_type(
        annotation: Annotation | type,
        custom_types: Iterable[type] = ()
) -> bool:
    """Return True if the annotation is a value type like an int or a str.

    Args:
        annotation (Any | type): The annotation
        custom_types (Iterable[type]): Any custom types.

    Returns:
        bool: True if the annotation is a JSON literal, otherwise False
    """
    return (
        annotation in BUILTIN_TYPES or
        annotation in custom_types or
        (isclass(annotation) and issubclass(annotation, Enum))
    )


def is_container_type(annotation: Any) -> bool:
    """Return True if this is a JSON container.

    A JSON container can be an object (Like a dict[str, Any]), or a list.

    Args:
        annotation (Any): The type annotation.

    Returns:
        bool: True if the annotation is represented in JSON as a container.
    """
    if is_optional(annotation):
        return all(is_container_type(t) for t in get_optional_types(annotation))
    else:
        return (
            is_list(annotation) or
            is_dict(annotation) or
            is_typeddict(annotation)
        )


def is_typed(annotation: Annotation) -> bool:
    return (
        is_typeddict(annotation) or
        (
            is_list(annotation) and
            is_typed(get_args(annotation)[0])
        ) or
        (
            is_annotated(annotation) and
            is_typed(get_annotated_type(annotation))
        )
    )
