"""Tests for the untyped deserializer"""

from datetime import timedelta, datetime

from stringcase import snakecase, camelcase

from jetblack_serialization.config import SerializerConfig
from jetblack_serialization.json.untyped_deserializer import deserialize_untyped

CONFIG = SerializerConfig(camelcase, snakecase)


def test_json_untyped_deserialize():
    """Tests for deserialize"""
    text = '{"strArg": "text", "intArg": 42, "floatArg": 3.14, "dateArg": "2019-12-31T23:59:59.00Z", "durationArg": "PT1H7M"}'
    obj = deserialize_untyped(text, CONFIG)
    assert obj == {
        'str_arg': 'text',
        'int_arg': 42,
        'float_arg': 3.14,
        'date_arg': datetime(2019, 12, 31, 23, 59, 59),
        'duration_arg': timedelta(hours=1, minutes=7)
    }
