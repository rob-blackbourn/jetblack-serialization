"""Tests for typing_import_ext"""

from datetime import datetime
from decimal import Decimal
import inspect
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Generic,
    Iterable,
    List,
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

import jetblack_serialization.typing_inspect_ex as typing_inspect


class MockDict(TypedDict):
    """A mock typed dict

    Args:
        arg_num1 (str): The first arg
        arg_num2 (List[int]): The second arg
        arg_num3 (datetime): The third arg
        arg_num4 (Optional[Decimal], optional): The fourth arg. Defaults to Decimal('1').
        arg_num5 (Optional[float], optional): The fifth arg. Defaults to None.
    """
    arg_num1: str
    arg_num2: List[int]
    arg_num3: datetime
    arg_num4: Optional[Decimal] = Decimal('1')  # type: ignore
    arg_num5: Optional[float] = None  # type: ignore


def func(
        dict_arg: Dict[str, Any],
        typed_dict_arg: MockDict,
        optional_dict_arg: Optional[Dict[str, Any]],
        optional_typed_dict_arg: Optional[MockDict],
        list_arg: List[str]
) -> None:
    pass


def test_is_typed_dict() -> None:
    signature = inspect.signature(func)
    typed_dict_arg_param = signature.parameters["typed_dict_arg"]
    assert typing_inspect.is_typed_dict_type(typed_dict_arg_param.annotation)
    dict_arg_param = signature.parameters["dict_arg"]
    assert not typing_inspect.is_typed_dict_type(dict_arg_param.annotation)


def test_is_dict() -> None:
    signature = inspect.signature(func)
    typed_dict_arg_param = signature.parameters["typed_dict_arg"]
    assert not typing_inspect.is_dict_type(typed_dict_arg_param.annotation)
    dict_arg_param = signature.parameters["dict_arg"]
    assert typing_inspect.is_dict_type(dict_arg_param.annotation)


def test_is_list() -> None:
    signature = inspect.signature(func)
    typed_dict_arg_param = signature.parameters["typed_dict_arg"]
    assert not typing_inspect.is_list_type(typed_dict_arg_param.annotation)
    list_arg_param = signature.parameters["list_arg"]
    assert typing_inspect.is_list_type(list_arg_param.annotation)


def test_get_optional() -> None:
    signature = inspect.signature(func)
    dict_arg_param = signature.parameters["dict_arg"]
    typed_dict_arg_param = signature.parameters["typed_dict_arg"]
    optional_dict_arg_param = signature.parameters["optional_dict_arg"]
    optional_typed_dict_arg_param = signature.parameters["optional_typed_dict_arg"]
    assert typing_inspect.get_optional_type(dict_arg_param.annotation) is None
    assert typing_inspect.get_optional_type(
        typed_dict_arg_param.annotation) is None
    assert typing_inspect.get_optional_type(
        optional_dict_arg_param.annotation) is Dict[str, Any]
    assert typing_inspect.get_optional_type(
        optional_typed_dict_arg_param.annotation) is MockDict


def run_sample(
        fun: Callable[[Any], bool],
        samples: List[Any],
        nonsamples: List[Any]
) -> None:
    for s in samples:
        assert fun(s)
    for s in nonsamples:
        assert not fun(s)


def test_generic() -> None:
    T = TypeVar('T')
    samples = [
        Generic,
        Generic[T],
        Iterable[int],
        Mapping,
        MutableMapping[T, List[int]],
        Sequence[Union[str, bytes]]
    ]
    nonsamples = [
        int,
        Union[int, str],
        Union[int, T],
        ClassVar[List[int]],
        Callable[..., T],
        ClassVar,
        Optional,
        bytes,
        list
    ]
    run_sample(typing_inspect.is_generic_type, samples, nonsamples)


def test_callable() -> None:
    samples = [
        Callable,
        Callable[..., int],
        Callable[[int, int],
                 Iterable[str]]
    ]
    nonsamples = [
        int,
        type,
        42,
        [],
        List[int],
        Union[callable, Callable[..., int]]
    ]
    run_sample(typing_inspect.is_callable_type, samples, nonsamples)

    class MyClass(Callable[[int], int]):
        pass
    assert typing_inspect.is_callable_type(MyClass)


def test_tuple() -> None:
    samples = [
        Tuple,
        Tuple[str, int],
        Tuple[Iterable, ...]
    ]
    nonsamples = [
        int,
        tuple,
        42,
        List[int],
        NamedTuple('N', [('x', int)])
    ]
    run_sample(typing_inspect.is_tuple_type, samples, nonsamples)

    class MyClass(Tuple[str, int]):
        pass
    assert typing_inspect.is_tuple_type(MyClass)


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
    run_sample(typing_inspect.is_union_type, samples, nonsamples)


def test_optional_type() -> None:
    T = TypeVar('T')
    samples = [
        type(None),                # none type
        Optional[int],             # direct union to none type 1
        Optional[T],               # direct union to none type 2
        Optional[T][int],          # direct union to none type 3
        Union[int, type(None)],    # direct union to none type 4
        Union[str, T][type(None)]  # direct union to none type 5
    ]
    # nested unions are supported
    samples += [
        Union[str, Optional[int]],      # nested Union 1
        Union[T, str][Optional[int]],   # nested Union 2
    ]
    nonsamples = [
        int,
        Union[int, int],
        [],
        Iterable[Any],
        T,
        Union[T, str][int]
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
    run_sample(typing_inspect.is_optional_type, samples, nonsamples)


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
    run_sample(typing_inspect.is_literal_type, samples, nonsamples)


def test_typevar() -> None:
    T = TypeVar('T')
    S_co = TypeVar('S_co', covariant=True)
    samples = [T, S_co]
    nonsamples = [int, Union[T, int], Union[T, S_co], type, ClassVar[int]]
    run_sample(typing_inspect.is_typevar, samples, nonsamples)


def test_classvar() -> None:
    T = TypeVar('T')
    samples = [ClassVar, ClassVar[int], ClassVar[List[T]]]
    nonsamples = [int, 42, Iterable, List[int], type, T]
    run_sample(typing_inspect.is_classvar, samples, nonsamples)


def test_origin() -> None:
    T = TypeVar('T')
    assert typing_inspect.get_origin(int) is None
    assert typing_inspect.get_origin(ClassVar[int]) is None
    assert typing_inspect.get_origin(Generic) is Generic
    assert typing_inspect.get_origin(Generic[T]) is Generic
    assert typing_inspect.get_origin(List[Tuple[T, T]][int]) is list


def test_parameters() -> None:
    T = TypeVar('T')
    S_co = TypeVar('S_co', covariant=True)
    U = TypeVar('U')
    assert typing_inspect.get_parameters(int) == ()
    assert typing_inspect.get_parameters(Generic) == ()
    assert typing_inspect.get_parameters(Union) == ()
    assert typing_inspect.get_parameters(List[int]) == ()
    assert typing_inspect.get_parameters(Generic[T]) == (T,)
    assert typing_inspect.get_parameters(
        Tuple[List[T], List[S_co]]) == (T, S_co)
    assert typing_inspect.get_parameters(
        Union[S_co, Tuple[T, T]][int, U]) == (U,)
    assert typing_inspect.get_parameters(
        Mapping[T, Tuple[S_co, T]]) == (T, S_co)


def test_args_evaluated() -> None:
    T = TypeVar('T')
    assert typing_inspect.get_args(
        Union[int, Tuple[T, int]][str],
        evaluate=True
    ) == (int, Tuple[str, int])
    assert typing_inspect.get_args(
        Dict[int, Tuple[T, T]][Optional[int]],
        evaluate=True
    ) == (int, Tuple[Optional[int], Optional[int]])
    assert typing_inspect.get_args(
        Callable[[], T][int], evaluate=True) == ([], int,)
    assert typing_inspect.get_args(
        Union[int, Callable[[Tuple[T, ...]], str]],
        evaluate=True
    ) == (int, Callable[[Tuple[T, ...]], str])

    # ClassVar special-casing
    assert typing_inspect.get_args(ClassVar, evaluate=True) == ()
    assert typing_inspect.get_args(ClassVar[int], evaluate=True) == (int,)

    # Literal special-casing
    assert typing_inspect.get_args(Literal, evaluate=True) == ()
    assert typing_inspect.get_args(
        Literal["value"], evaluate=True) == ("value",)
    assert typing_inspect.get_args(
        Literal[1, 2, 3], evaluate=True) == (1, 2, 3)


def test_bound() -> None:
    T = TypeVar('T')
    TB = TypeVar('TB', bound=int)
    assert typing_inspect.get_bound(T) == None
    assert typing_inspect.get_bound(TB) == int


def test_constraints() -> None:
    T = TypeVar('T')
    TC = TypeVar('TC', int, str)
    assert typing_inspect.get_constraints(T) == ()
    assert typing_inspect.get_constraints(TC) == (int, str)


def test_generic_type() -> None:
    T = TypeVar('T')

    class Node(Generic[T]):
        pass
    assert typing_inspect.get_generic_type(Node()) is Node
    assert typing_inspect.get_generic_type(Node[int]()) is Node[int]
    assert typing_inspect.get_generic_type(Node[T]()) is Node[T]
    assert typing_inspect.get_generic_type(1) is int


def test_generic_bases() -> None:
    class MyClass(List[int], Mapping[str, List[int]]):  # type: ignore
        pass
    assert typing_inspect.get_generic_bases(
        MyClass
    ) == (List[int], Mapping[str, List[int]])
    assert typing_inspect.get_generic_bases(int) == ()
