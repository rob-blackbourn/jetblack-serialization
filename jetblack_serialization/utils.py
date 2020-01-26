"""Protocol utilities"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import jetblack_serialization.typing_inspect_ex as typing_inspect
from .types import Annotation


def is_simple_type(annotation: Annotation) -> bool:
    """Return True if the annotation is a simple type like an int or a str.

    Args:
        annotation (Any): The annotation

    Returns:
        bool: True if the annotation is a JSON literal, otherwise False
    """
    return annotation in (
        str,
        bool,
        int,
        float,
        Decimal,
        datetime,
        timedelta
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
