from collections.abc import Callable
from inspect import isclass
from types import (
    NoneType,
    UnionType
)
from typing import (
    Annotated,
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Tuple,
    TypeVar,
    Union,
    is_typeddict,
    get_args,
    get_origin
)


def _get_origin_not_none(annotation: type[Any]) -> type[Any]:
    origin = get_origin(annotation)
    if origin is None:
        raise TypeError(f"Annotation {annotation} has no origin.")
    return origin


def is_union(annotation: type[Any]) -> bool:
    return annotation is Union or get_origin(annotation) in (Union, UnionType)


def is_optional(annotation: type[Any]) -> bool:
    return (
        is_union(annotation) and
        any(arg is NoneType for arg in get_args(annotation))
    )


def get_optional_type(annotation: type[Any]) -> type[Any] | None:
    # TODO: return a tuple.
    if not is_optional(annotation):
        return None
    contained_type, *_rest = get_args(annotation)
    return contained_type


def is_annotated(annotation: type[Any]) -> bool:
    return get_origin(annotation) is Annotated


def get_unannotated(annotation: type[Any]) -> type[Any]:
    while is_annotated(annotation):
        annotation = _get_origin_not_none(annotation)
    return annotation


def is_generic(annotation: type[Any]) -> bool:
    origin = get_origin(annotation)
    return origin is not None and not (
        origin is Union or origin is UnionType or origin is Callable
    )


def is_list(annotation: type[Any]) -> bool:
    return annotation in (list, List) or get_origin(annotation) in (list, List)


def is_dict(annotation: type[Any]) -> bool:
    return annotation in (dict, Dict) or get_origin(annotation) in (dict, Dict)


def is_callable(annotation: type[Any]) -> bool:
    return annotation is Callable or get_origin(annotation) is Callable


def is_tuple(annotation: type) -> bool:
    """Return True if annotation is a tuple or a generic tuple.

    Allows:

    - `tuple`
    - `Tuple`
    - `Tuple[int, str]`
    - `tuple[int, str]`
    - `NamedTuple('N', [('x', int)])`

    Args:
        annotation (type[Any]): The type annotation to check.

    Returns:
        bool: True if the annotation is a tuple or a generic tuple, False otherwise.
    """
    return (
        annotation is tuple
        or annotation is Tuple
        or (isclass(annotation) and issubclass(annotation, tuple)) or
        get_origin(annotation) is tuple  # For NamedTuple.
    )


def is_literal(annotation: type) -> bool:
    origin = get_origin(annotation)
    return annotation is Literal or origin is Literal


def is_typevar(annotation: type[Any]) -> bool:
    """Return True if annotation is a TypeVar."""
    return isinstance(annotation, TypeVar)


def is_classvar(annotation: type[Any]) -> bool:
    """Return True if annotation is a TypeVar."""
    origin = get_origin(annotation)
    return annotation is ClassVar or origin is ClassVar


def typeddict_keys(annotation: type) -> dict[str, type]:
    assert is_typeddict(annotation)
    return annotation.__annotations__.copy()


def get_metadata(annotation: type) -> tuple[Any, ...] | None:
    return getattr(annotation, '__metadata__', None)
