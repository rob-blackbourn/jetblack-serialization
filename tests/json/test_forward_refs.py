from __future__ import annotations

from typing import NotRequired, TypedDict

from jetblack_serialization.json import serialize, deserialize


class Foo(TypedDict):
    name: NotRequired[str]
    bars: list[Bar]


class Bar(TypedDict):
    name: str


def test_forward_refs() -> None:
    data = {
        'name': 'foo',
        'bars': [
            {'name': 'mary'},
            {'name': 'alberto'},
        ]
    }
    text = serialize(data, Foo)
    roundtrip = deserialize(text, Foo)
    assert roundtrip == data
