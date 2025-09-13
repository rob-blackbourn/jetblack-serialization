from datetime import datetime
from typing import Annotated, NotRequired, TypedDict

from jetblack_serialization import DefaultValue, DefaultFactory
from jetblack_serialization.json import serialize_typed, deserialize_typed


class Example(TypedDict, total=False):
    a: int
    b: NotRequired[Annotated[str, DefaultValue("default")]]
    c: Annotated[datetime, DefaultFactory(datetime.now)]


def test_default_factory() -> None:
    original = Example(a=1)
    text = serialize_typed(original, Example)
    roundtrip = deserialize_typed(text, Example)
    assert 'c' not in original
    assert 'c' in roundtrip and isinstance(roundtrip['c'], datetime)
