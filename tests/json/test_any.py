from typing import Any, TypedDict

from jetblack_serialization.json import serialize_typed, deserialize_typed


class Example(TypedDict):
    value: Any


def test_any_dict() -> None:
    actual = Example(value='foo')
    text = serialize_typed(actual, Example)
    roundtrip = deserialize_typed(text, Example)
    assert actual == roundtrip


def test_any_list() -> None:
    actual = Example(value=[1, 2, 3])
    text = serialize_typed(actual, Example)
    roundtrip = deserialize_typed(text, Example)
    assert actual == roundtrip
