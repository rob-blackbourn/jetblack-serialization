"""Tests for typing_import_ext"""

from datetime import datetime
from decimal import Decimal
import inspect
import typing
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    Literal,
    Mapping,
    MutableMapping,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    TypeVar,
    Union
)

import jetblack_serialization.typing_ex as typing_ex


class MockDict(TypedDict):
    """A mock typed dict

    Args:
        arg_num1 (str): The first arg
        arg_num2 (list[int]): The second arg
        arg_num3 (datetime): The third arg
        arg_num4 (Decimal | None, optional): The fourth arg. Defaults to Decimal('1').
        arg_num5 (float | None, optional): The fifth arg. Defaults to None.
    """
    arg_num1: str
    arg_num2: list[int]
    arg_num3: datetime
    arg_num4: Decimal | None = Decimal('1')  # type: ignore
    arg_num5: float | None = None  # type: ignore


def func(
        dict_arg: dict[str, Any],
        typed_dict_arg: MockDict,
        optional_dict_arg: Optional[Dict[str, Any]],
        optional_typed_dict_arg: Optional[MockDict],
        list_arg: list[str]
) -> None:
    pass


def test_is_typed_dict() -> None:
    signature = inspect.signature(func)
    typed_dict_arg_param = signature.parameters["typed_dict_arg"]
    assert typing.is_typeddict(typed_dict_arg_param.annotation)
    dict_arg_param = signature.parameters["dict_arg"]
    assert not typing.is_typeddict(dict_arg_param.annotation)


def test_is_dict() -> None:
    signature = inspect.signature(func)
    typed_dict_arg_param = signature.parameters["typed_dict_arg"]
    assert not typing_ex.is_dict(typed_dict_arg_param.annotation)
    dict_arg_param = signature.parameters["dict_arg"]
    assert typing_ex.is_dict(dict_arg_param.annotation)


def test_is_list() -> None:
    signature = inspect.signature(func)
    typed_dict_arg_param = signature.parameters["typed_dict_arg"]
    assert not typing_ex.is_list(typed_dict_arg_param.annotation)
    list_arg_param = signature.parameters["list_arg"]
    assert typing_ex.is_list(list_arg_param.annotation)


def test_get_optional() -> None:
    signature = inspect.signature(func)
    optional_dict_arg_param = signature.parameters["optional_dict_arg"]
    optional_typed_dict_arg_param = signature.parameters["optional_typed_dict_arg"]
    assert typing_ex.get_optional_types(
        optional_dict_arg_param.annotation) == (Dict[str, Any],)
    assert typing_ex.get_optional_types(
        optional_typed_dict_arg_param.annotation) == (MockDict,)


def run_sample(
        fun: Callable[[Any], bool],
        samples: list[Any],
        nonsamples: list[Any]
) -> None:
    for s in samples:
        assert fun(s)
    for s in nonsamples:
        assert not fun(s)


def test_generic() -> None:
    T = TypeVar('T')
    samples = [
        ClassVar[list[int]],
        Generic,
        Generic[T],
        Iterable[int],
        Mapping,
        MutableMapping[T, list[int]],
        Sequence[Union[str, bytes]]
    ]
    nonsamples = [
        int,
        ClassVar,
        Union[int, str],
        Union[int, T],
        Callable[..., T],
        Optional,
        bytes,
        list
    ]
    run_sample(typing_ex.is_generic, samples, nonsamples)


def test_callable() -> None:
    samples = [
        Callable,
        Callable[..., int],
        Callable[[int, int], Iterable[str]]
    ]
    nonsamples = [
        int,
        type,
        42,
        [],
        list[int],
        Union[callable, Callable[..., int]]
    ]
    run_sample(typing_ex.is_callable, samples, nonsamples)


def test_tuple() -> None:
    samples = [
        tuple,
        Tuple,
        Tuple[str, int],
        Tuple[Iterable, ...],
        NamedTuple('N', [('x', int)])
    ]
    nonsamples = [
        int,
        42,
        list[int],
    ]
    run_sample(typing_ex.is_tuple, samples, nonsamples)

    class MyClass(Tuple[str, int]):
        pass
    assert typing_ex.is_tuple(MyClass)


def test_union() -> None:
    T = TypeVar('T')
    S = TypeVar('S')
    samples = [
        Union,
        Union[T, int],
        Union[int, Union[T, S]]
    ]
    nonsamples = [
        int,
        Union[int, int],
        [],
        Iterable[Any]
    ]
    run_sample(typing_ex.is_union, samples, nonsamples)


def test_optional_type() -> None:
    T = TypeVar('T')
    samples = [
        Optional[int],             # direct union to none type 1
        Optional[T],               # direct union to none type 2
        Optional[T][int],          # direct union to none type 3
        Union[int, type(None)],    # direct union to none type 4
    ]
    # nested unions are supported
    samples += [
        Union[str, Optional[int]],      # nested Union 1
    ]
    nonsamples = [
        int,
        Union[int, int],
        [],
        Iterable[Any],
        T,
    ]
    # unfortunately current definition sets these ones as non samples too
    S1 = TypeVar('S1', bound=Optional[int])
    S2 = TypeVar('S2', type(None), str)
    S3 = TypeVar('S3', Optional[int], str)
    S4 = TypeVar('S4', bound=Union[str, Optional[int]])
    nonsamples += [
        S1, S2, S3,                     # typevar bound or constrained to optional
        Union[S1, int], S4              # combinations of the above
    ]
    run_sample(typing_ex.is_optional, samples, nonsamples)


def test_literal_type() -> None:
    samples = [
        Literal,
        Literal["v"],
        Literal[1, 2, 3],
    ]
    nonsamples = [
        "v",
        (1, 2, 3),
        int,
        str,
        Union["u", "v"],
    ]
    run_sample(typing_ex.is_literal, samples, nonsamples)


def test_typevar() -> None:
    T = TypeVar('T')
    S_co = TypeVar('S_co', covariant=True)
    samples = [T, S_co]
    nonsamples = [int, Union[T, int], Union[T, S_co], type, ClassVar[int]]
    run_sample(typing_ex.is_typevar, samples, nonsamples)


def test_classvar() -> None:
    T = TypeVar('T')
    samples = [ClassVar, ClassVar[int], ClassVar[list[T]]]
    nonsamples = [int, 42, Iterable, list[int], type, T]
    run_sample(typing_ex.is_classvar, samples, nonsamples)
