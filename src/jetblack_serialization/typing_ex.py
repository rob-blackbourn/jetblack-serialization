from collections.abc import Callable
from dataclasses import dataclass
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
    ForwardRef,
    List,
    Literal,
    Required,
    NotRequired,
    Self,
    Tuple,
    TypeAliasType,
    TypeVar,
    Union,
    is_typeddict,
    get_args,
    get_origin
)


def is_type_alias(annotation: Any) -> bool:
    return isinstance(annotation, TypeAliasType)


def resolve_type_alias(annotation: Any) -> Any:
    return (
        annotation.__value__
        if is_type_alias(annotation) else
        annotation
    )


def is_forward_ref(annotation: type[Any]) -> bool:
    return isinstance(annotation, ForwardRef)


def resolve_forward_ref(annotation: Any) -> Any:
    return (
        annotation._evaluate(  # pylint: disable=protected-access
            globals(),
            locals(),
            recursive_guard=frozenset()
        )
        if is_forward_ref(annotation) else
        annotation
    )


def resolve_type(annotation: Any) -> Any:
    annotation = resolve_forward_ref(annotation)
    annotation = resolve_type_alias(annotation)
    return annotation


def is_any(annotation: type[Any]) -> bool:
    return annotation is Any


def is_union(annotation: type[Any]) -> bool:
    return annotation is Union or get_origin(annotation) in (Union, UnionType)


def is_optional(annotation: type[Any]) -> bool:
    return (
        is_union(annotation) and
        any(arg is NoneType for arg in get_args(annotation))
    )


def get_optional_types(annotation: type) -> tuple[type, ...]:
    assert is_optional(annotation)
    return tuple(
        resolve_type(t)
        for t in get_args(annotation)
        if t is not NoneType
    )


def is_annotated(annotation: type[Any]) -> bool:
    return get_origin(annotation) is Annotated


def get_annotated_type(annotation: Annotated[Any, ...]) -> type:
    return resolve_type(annotation.__origin__)


def get_unannotated(annotation: type[Any]) -> type[Any]:
    while is_annotated(annotation):
        annotation = get_annotated_type(annotation)
    return resolve_type(annotation)


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


@dataclass
class TypedDictFieldInfo:
    annotation: type
    is_required: bool

    @classmethod
    def create(cls, annotation: Any, total: bool) -> Self:
        annotation = resolve_type(annotation)

        if is_generic(annotation) and get_origin(annotation) is NotRequired:
            annotation = get_args(annotation)[0]
            is_required = False
        elif is_generic(annotation) and get_origin(annotation) is Required:
            annotation = get_args(annotation)[0]
            is_required = True
        else:
            is_required = total

        return cls(
            annotation=annotation,
            is_required=is_required
        )


def typeddict_keys(annotation: type) -> dict[str, TypedDictFieldInfo]:
    assert is_typeddict(annotation)
    is_total = getattr(annotation, '__total__', True)
    return {
        key: TypedDictFieldInfo.create(field_type, is_total)
        for key, field_type in annotation.__annotations__.items()
    }


def get_metadata(annotation: type) -> tuple[Any, ...] | None:
    return getattr(annotation, '__metadata__', None)
