from typing import TypedDict

from stringcase import snakecase, camelcase

from jetblack_serialization import SerializerConfig
from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
)


class Example(TypedDict):
    short_name: str
    long_name: str


def test_key_serializarion() -> None:

    config = SerializerConfig(
        key_serializer=camelcase,
        key_deserializer=snakecase,
    )

    orig: Example = {
        'short_name': 'rtb',
        'long_name': 'Robert Thomas Blackbourn',
    }

    text = serialize_typed(orig, Example, config)
    assert text == '{"shortName": "rtb", "longName": "Robert Thomas Blackbourn"}'

    roundtrip1 = deserialize_typed(text, Example, config)
    assert orig == roundtrip1
