"""Round trip tests for XML serialization"""

from datetime import datetime, timedelta
from decimal import Decimal

from stringcase import pascalcase, snakecase


from jetblack_serialization.config import SerializerConfig
from jetblack_serialization.xml.untyped_deserializer import deserialize_untyped

CONFIG = SerializerConfig(pascalcase, snakecase)


def test_untyped_xml_serialization_simple():
    config = SerializerConfig(pascalcase, snakecase)

    int_text = '<object type="int">42</object>'
    int_obj = deserialize_untyped(int_text, config)
    assert int_obj == 42

    str_text = '<object type="str">42</object>'
    str_obj = deserialize_untyped(str_text, config)
    assert str_obj == '42'

    float_text = '<object type="float">42.0</object>'
    float_obj = deserialize_untyped(float_text, config)
    assert float_obj == 42.0

    decimal_text = '<object type="Decimal">42.0</object>'
    decimal_obj = deserialize_untyped(decimal_text, config)
    assert decimal_obj == Decimal('42.0')

    datetime_text = '<object type="datetime">2020-01-01T12:32:59.999Z</object>'
    datetime_obj = deserialize_untyped(datetime_text, config)
    assert datetime_obj == datetime(2020, 1, 1, 12, 32, 59, 999000)

    timedelta_text = '<object type="timedelta">P1M10DT3H15M35S</object>'
    timedelta_obj = deserialize_untyped(timedelta_text, config)
    assert timedelta_obj == timedelta(days=40, hours=3, minutes=15, seconds=35)

def test_untyped_xml_serialization_list():
    config = SerializerConfig(pascalcase, snakecase)

    list_int_text = '<object type="list"><object type="int">1</object><object type="int">2</object><object type="int">3</object></object>'
    list_int_obj = deserialize_untyped(list_int_text, config)
    assert list_int_obj == [1, 2, 3]

def test_untyped_xml_serialization_dict():
    config = SerializerConfig(pascalcase, snakecase)

    text = (
        '<object type="dict">'
            '<object type="dict-entry">'
                '<object type="str" role="key">int</object>'
                '<object type="int" role="value">42</object>'
            '</object>'
            '<object type="dict-entry">'
                '<object type="str" role="key">str</object>'
                '<object type="str" role="value">a string</object>'
                '</object>'
            '<object type="dict-entry">'
                '<object type="str" role="key">list</object>'
                '<object type="list" role="value">'
                    '<object type="int">1</object>'
                    '<object type="int">2</object>'
                    '<object type="int">3</object>'
                '</object>'
            '</object>'
            '<object type="dict-entry">'
                '<object type="str" role="key">dict</object>'
                '<object type="dict" role="value">'
                    '<object type="dict-entry">'
                        '<object type="str" role="key">one</object>'
                        '<object type="int" role="value">1</object>'
                    '</object>'
                    '<object type="dict-entry">'
                        '<object type="str" role="key">two</object>'
                        '<object type="int" role="value">2</object>'
                    '</object>'
                '</object>'
            '</object>'
        '</object>'
    )
    obj = deserialize_untyped(text, config)
    assert obj == {
        'int': 42,
        'str': 'a string',
        'list': [1, 2, 3],
        'dict': {
            'one': 1,
            'two': 2
        }
    }
