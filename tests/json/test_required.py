from typing import Annotated, NotRequired, Required, TypedDict

from stringcase import snakecase, camelcase

from jetblack_serialization import SerializerConfig
from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
    JSONProperty
)

CONFIG = SerializerConfig(
    key_serializer=camelcase,
    key_deserializer=snakecase,
)


class OptInExample(TypedDict, total=False):
    first_arg: Annotated[int, JSONProperty("argA")]
    second_arg: NotRequired[str]
    third_arg: Required[float]


class OptOutExample(TypedDict, total=True):
    first_arg: int
    second_arg: NotRequired[str]
    third_arg: Required[float]


def test_required_opt_in() -> None:
    opt_in_obj: OptInExample = {'first_arg': 1, 'third_arg': 2.0}
    opn_in_text = serialize_typed(opt_in_obj, OptInExample, CONFIG)
    opt_in_roundtrip = deserialize_typed(opn_in_text, OptInExample, CONFIG)
    assert opt_in_obj == opt_in_roundtrip


def test_required_opt_out() -> None:
    opt_out_obj: OptOutExample = {'first_arg': 1, 'third_arg': 2.0}
    opn_out_text = serialize_typed(opt_out_obj, OptOutExample, CONFIG)
    opt_out_roundtrip = deserialize_typed(opn_out_text, OptOutExample, CONFIG)
    assert opt_out_obj == opt_out_roundtrip
