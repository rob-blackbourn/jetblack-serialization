"""Tests for custom_annotations.py"""

import inspect

from typing import Annotated

from jetblack_serialization.custom_annotations import (
    SerializationAnnotation,
    is_any_serialization_annotation,
    get_all_serialization_annotations,
    DefaultValue,
    is_any_default_annotation,
    get_default_annotation
)


class FooAnnotation(SerializationAnnotation):
    """A serialization annotation for Foo"""


class BarAnnotation(SerializationAnnotation):
    """A serialization annotation for Bar"""


def test_serialization_annotations() -> None:
    def func(
            arg1,
            arg2: int,
            arg3: Annotated[int, FooAnnotation()],
            arg4: Annotated[int, BarAnnotation()],
            arg5: Annotated[int, FooAnnotation(), BarAnnotation()],
    ) -> None:
        pass

    signature = inspect.signature(func)
    arg1_dict_arg_param = signature.parameters["arg1"]
    assert not is_any_serialization_annotation(arg1_dict_arg_param.annotation)

    arg2_dict_arg_param = signature.parameters["arg2"]
    assert not is_any_serialization_annotation(arg2_dict_arg_param.annotation)

    arg3_dict_arg_param = signature.parameters["arg3"]
    assert is_any_serialization_annotation(arg3_dict_arg_param.annotation)
    _, annotations = get_all_serialization_annotations(
        arg3_dict_arg_param.annotation)
    assert len(annotations) == 1

    arg4_dict_arg_param = signature.parameters["arg4"]
    assert is_any_serialization_annotation(arg4_dict_arg_param.annotation)
    _, annotations = get_all_serialization_annotations(
        arg4_dict_arg_param.annotation)
    assert len(annotations) == 1

    arg5_dict_arg_param = signature.parameters["arg5"]
    assert is_any_serialization_annotation(arg5_dict_arg_param.annotation)
    _, annotations = get_all_serialization_annotations(
        arg5_dict_arg_param.annotation)
    assert len(annotations) == 2


def test_default_annotations() -> None:
    def func(
            arg1,
            arg2: int,
            arg3: Annotated[int, DefaultValue(42)]
    ) -> None:
        pass

    signature = inspect.signature(func)

    arg1_dict_arg_param = signature.parameters["arg1"]
    assert not is_any_default_annotation(arg1_dict_arg_param.annotation)

    arg2_dict_arg_param = signature.parameters["arg2"]
    assert not is_any_default_annotation(arg2_dict_arg_param.annotation)

    arg3_dict_arg_param = signature.parameters["arg3"]
    assert is_any_default_annotation(arg3_dict_arg_param.annotation)
    _, annotation = get_default_annotation(arg3_dict_arg_param.annotation)
    assert annotation.value == 42
