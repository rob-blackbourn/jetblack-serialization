from datetime import datetime
from typing import Annotated, Any, TypedDict

from stringcase import snakecase, camelcase

from jetblack_serialization import SerializerConfig
from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
    JSONObject
)

CONFIG = SerializerConfig(
    key_serializer=camelcase,
    key_deserializer=snakecase,
)


class Foo(TypedDict):
    x: int


class Example1(TypedDict, total=False):
    a: dict[str, Foo]


def test_dict_in_typed() -> None:
    original = Example1(a={'one': {'x': 1}, 'two': {'x': 2}})
    text = serialize_typed(original, Example1)
    roundtrip = deserialize_typed(text, Example1)
    assert original == roundtrip


class Example2(TypedDict):
    one: dict[str, int]
    two: Annotated[dict[str, int], JSONObject(is_serializable_keys=False)]
    three: Annotated[dict[str, int], JSONObject(is_serializable_keys=True)]


def test_dict_keys() -> None:
    original: Example2 = {
        'one': {'first_key': 1, 'second_key': 2},
        'two': {'first_key': 1, 'second_key': 2},
        'three': {'first_key': 1, 'second_key': 2},
    }
    text = serialize_typed(original, Example2, CONFIG)
    roundtrip = deserialize_typed(text, Example2, CONFIG)
    assert original == roundtrip
