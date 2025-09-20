from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import TypedDict
import urllib.parse
from zoneinfo import ZoneInfo

from stringcase import snakecase, camelcase

from jetblack_serialization import (
    SerializerConfig,
    ValueDeserializers,
    ValueSerializers,
    VALUE_DESERIALIZERS,
    VALUE_SERIALIZERS
)
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
    event_date: date
    event_time: time
    event_timezone: ZoneInfo


def test_value_serialization() -> None:

    london = ZoneInfo('Europe/London')

    orig: ValueExample = {
        'distance': Decimal('1234.5'),
        'timestamp': datetime(2024, 6, 1, 12, 0, 0, tzinfo=london),
        'delay': timedelta(hours=1, minutes=30),
        'event_date': date(2000, 1, 1),
        'event_time': time(23, 15, 37),
        'event_timezone': ZoneInfo('Europe/London'),
    }

    text = serialize_typed(orig, ValueExample)
    assert text == (
        '{"distance": 1234.5, '
        '"timestamp": "2024-06-01T12:00:00.00+01:00", '
        '"delay": "PT1H30M", '
        '"event_date": "2000-01-01", '
        '"event_time": "23:15:37", '
        '"event_timezone": "Europe/London"}'
    )

    roundtrip1 = deserialize_typed(text, ValueExample)
    assert orig == roundtrip1


class CustomValueExample(TypedDict):
    url: urllib.parse.ParseResult


def test_custom_value_serialization() -> None:

    value_serializers: ValueSerializers = (
        *VALUE_SERIALIZERS,
        (urllib.parse.ParseResult, lambda d: d.geturl()),
    )
    value_deserializers: ValueDeserializers = (
        *VALUE_DESERIALIZERS,
        (urllib.parse.ParseResult, urllib.parse.urlparse),
    )

    config = SerializerConfig(
        value_serializers=value_serializers,
        value_deserializers=value_deserializers,
    )
    orig: CustomValueExample = {
        'url': urllib.parse.urlparse('https://example.com/path?query=1'),
    }

    text = serialize_typed(orig, CustomValueExample, config)
    assert text == '{"url": "https://example.com/path?query=1"}'

    roundtrip1 = deserialize_typed(text, CustomValueExample, config)
    assert orig == roundtrip1
