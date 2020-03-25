"""Extensions for typing_inspect"""

try:
    # Python3.8
    from typing import _TypedDictMeta  # type: ignore
except:
    # Python3.7
    from typing_extensions import _TypedDictMeta  # type: ignore
from typing_extensions import _AnnotatedAlias  # type: ignore# pylint: disable=unused-import
from typing_inspect import (
    get_args,
    get_bound,
    get_constraints,
    get_generic_bases,
    get_generic_type,
    get_last_args,
    get_last_origin,
    get_origin,
    get_parameters,
    is_callable_type,
    is_classvar,
    is_generic_type,
    is_literal_type,
    is_optional_type,
    is_tuple_type,
    is_typevar,
    is_union_type
)


def is_typed_dict_type(annotation):
    """Test for a typed dictionary

    Args:
        annotation ([type]): The type annotation

    Returns:
        bool: True if the type annotation was for a typed dict
    """
    return isinstance(annotation, _TypedDictMeta)


def is_list_type(annotation):
    """Return True if the annotation if for a List"""
    return (
        get_origin(annotation) is list
        and getattr(annotation, '_name', None) == 'List'
    )


def is_annotated_type(annotation):
    return isinstance(annotation, _AnnotatedAlias)


def get_metadata(annotation):
    return getattr(annotation, '__metadata__', None)


def get_optional_type(annotation):
    """Get the nested type annotation T for an Optional[T]"""
    if not is_optional_type(annotation):
        return None
    contained_type, *_rest = get_args(annotation)
    return contained_type


def is_dict_type(annotation):
    """Return True if the annotation if for a Dict"""
    return (
        get_origin(annotation) is dict
        and getattr(annotation, '_name', None) == 'Dict'
    )


def typed_dict_keys(td):
    """If td is a TypedDict class, return a dictionary mapping the typed keys to types.
    Otherwise, return None. Examples::

        class TD(TypedDict):
            x: int
            y: int
        class Other(dict):
            x: int
            y: int

        typed_dict_keys(TD) == {'x': int, 'y': int}
        typed_dict_keys(dict) == None
        typed_dict_keys(Other) == None
    """
    if isinstance(td, _TypedDictMeta):
        return td.__annotations__.copy()
    return None
