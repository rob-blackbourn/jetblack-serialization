from typing import TypedDict

from jetblack_serialization.json import serialize_typed, deserialize_typed


class Foo(TypedDict):
    x: int


class Example(TypedDict, total=False):
    a: dict[str, Foo]


def test_dict_in_typed() -> None:
    original = Example(a={'one': {'x': 1}, 'two': {'x': 2}})
    text = serialize_typed(original, Example)
    roundtrip = deserialize_typed(text, Example)
    assert original == roundtrip
