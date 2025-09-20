from datetime import datetime, timedelta
from decimal import Decimal
from typing import TypedDict
from zoneinfo import ZoneInfo

from stringcase import snakecase, camelcase

from jetblack_serialization import SerializerConfig
from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
)


class KeyExample(TypedDict):
    short_name: str
    long_name: str


def test_key_serializarion() -> None:

    config = SerializerConfig(
        key_serializer=camelcase,
        key_deserializer=snakecase,
    )

    orig: KeyExample = {
        'short_name': 'rtb',
        'long_name': 'Robert Thomas Blackbourn',
    }

    text = serialize_typed(orig, KeyExample, config)
    assert text == '{"shortName": "rtb", "longName": "Robert Thomas Blackbourn"}'

    roundtrip1 = deserialize_typed(text, KeyExample, config)
    assert orig == roundtrip1


class ValueExample(TypedDict):
    distance: Decimal
    timestamp: datetime
    delay: timedelta


def test_value_serialization() -> None:

    london = ZoneInfo('Europe/London')

    orig: ValueExample = {
        'distance': Decimal('1234.5'),
        'timestamp': datetime(2024, 6, 1, 12, 0, 0, tzinfo=london),
        'delay': timedelta(hours=1, minutes=30),
    }

    text = serialize_typed(orig, ValueExample)
    assert text == (
        '{"distance": 1234.5, '
        '"timestamp": "2024-06-01T12:00:00.00+01:00", '
        '"delay": "PT1H30M"}'
    )

    roundtrip1 = deserialize_typed(text, ValueExample)
    assert orig == roundtrip1
