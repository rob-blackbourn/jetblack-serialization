"""Extensions for typing_inspect"""

try:
    # Python3.8
    from typing import _TypedDictMeta  # type: ignore
except:  # pylint: disable=bare-except
    # Python3.7
    from typing_extensions import _TypedDictMeta  # type: ignore
# type: ignore# pylint: disable=unused-import
from typing_extensions import _AnnotatedAlias
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
    # is_optional_type,
    is_tuple_type,
    is_typevar,
    is_union_type
)


def is_typed_dict_type(tp):
    """Return True if tp is a typed dict"""
    return isinstance(tp, _TypedDictMeta)


def is_list_type(tp):
    """Return True if tp is a list"""
    return (
        get_origin(tp) is list
        and getattr(tp, '_name', None) == 'List'
    )


def is_annotated_type(tp):
    return isinstance(tp, _AnnotatedAlias)


def get_metadata(annotation):
    return getattr(annotation, '__metadata__', None)


def get_optional_type(annotation):
    """Get the nested type annotation T for an Optional[T]"""
    if not is_optional_type(annotation):
        return None
    contained_type, *_rest = get_args(annotation)
    return contained_type


def is_dict_type(tp):
    """Return True if tp is a Dict"""
    return (
        get_origin(tp) is dict
        and getattr(tp, '_name', None) == 'Dict'
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


def get_unannotated_type(tp):
    while is_annotated_type(tp):
        tp = get_origin(tp)
    return tp


def is_optional_type(tp):
    """Test if the type is type(None), or is a direct union with it, such as Optional[T].

    NOTE: this method inspects nested `Union` arguments but not `TypeVar` definition
    bounds and constraints. So it will return `False` if
     - `tp` is a `TypeVar` bound, or constrained to, an optional type
     - `tp` is a `Union` to a `TypeVar` bound or constrained to an optional type,
     - `tp` refers to a *nested* `Union` containing an optional type or one of the above.

    Users wishing to check for optionality in types relying on type variables might wish
    to use this method in combination with `get_constraints` and `get_bound`
    """

    if tp is type(None):  # noqa
        return True
    elif is_union_type(tp):
        return any(is_optional_type(tt) for tt in get_args(tp, evaluate=True))
    elif is_annotated_type(tp):
        return is_optional_type(get_unannotated_type(tp))
    else:
        return False
