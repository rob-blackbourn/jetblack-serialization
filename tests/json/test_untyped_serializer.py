"""Tests for the untyped serializer"""

from datetime import timedelta, datetime

from stringcase import snakecase, camelcase

from jetblack_serialization.config import SerializerConfig
from jetblack_serialization.json import serialize_untyped

CONFIG = SerializerConfig(serialize_key=camelcase, deserialize_key=snakecase)


def test_json_untyped_serialize() -> None:
    """Tests for serialize"""
    dct = {
        'str_arg': 'text',
        'int_arg': 42,
        'float_arg': 3.14,
        'date_arg': datetime(2019, 12, 31, 23, 59, 59),
        'duration_arg': timedelta(hours=1, minutes=7)
    }
    text = serialize_untyped(dct, CONFIG)
    assert text == '{"strArg": "text", "intArg": 42, "floatArg": 3.14, "dateArg": "2019-12-31T23:59:59.00Z", "durationArg": "PT1H7M"}'
