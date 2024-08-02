"""Protocol utilities"""

from enum import Enum
from inspect import isclass
from typing import Any, Iterable, Sequence, Type, Union

import jetblack_serialization.typing_inspect_ex as typing_inspect
from .types import Annotation

BUILTIN_TYPES: Sequence[Type] = (
    str,
    bool,
    int,
    float
)


def is_value_type(
        annotation: Union[Annotation, Type],
        custom_types: Iterable[Type]
) -> bool:
    """Return True if the annotation is a value type like an int or a str.

    Args:
        annotation (Union[Any, Type]): The annotation
        custom_types (Iterable[Type]): Any custom types.

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

    A JSON container can be an object (Like a Dict[str, Any]), or a List.

    Args:
        annotation (Any): The type annotation.

    Returns:
        bool: True if the annotation is represented in JSON as a container.
    """
    if typing_inspect.is_optional_type(annotation):
        return is_container_type(typing_inspect.get_optional_type(annotation))
    else:
        return (
            typing_inspect.is_list_type(annotation) or
            typing_inspect.is_dict_type(annotation) or
            typing_inspect.is_typed_dict_type(annotation)
        )
