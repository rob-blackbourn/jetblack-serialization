from typing import Literal, TypedDict

from jetblack_serialization.json import serialize_typed, deserialize_typed


class Example(TypedDict):
    scheme: Literal['http', 'https', 'ws', 'wss']


def test_literal() -> None:
    original = Example(scheme='http')
    text = serialize_typed(original, Example)
    roundtrip = deserialize_typed(text, Example)
    assert original == roundtrip
