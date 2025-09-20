# Configuration

The serializers/deserializers take a configuration object.
This contains functions to serialize and deserialize keys,
and dictionaries to serialize and deserialize values, keyed
by the value types.

## Keys

By default the key serializers and deserializers do not alter the keys.

A common pattern would be to serialize keys to camel-case and deserialize to
snake-case. There are a number of packages that do this; the example below uses
[stringcase](https://github.com/okunishinishi/python-stringcase).

```python
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


config = SerializerConfig(
    key_serializer=camelcase,
    key_deserializer=snakecase,
)

# In Python the keys are snake case.
orig: Example = {
    'short_name': 'rtb',
    'long_name': 'Robert Thomas Blackbourn',
}

# The JSON serialization converts the keys to camel case.
text = serialize_typed(orig, Example, config)
assert text == '{"shortName": "rtb", "longName": "Robert Thomas Blackbourn"}'

# Deserializing from JSON returns the keys to snake case.
roundtrip1 = deserialize_typed(text, Example, config)
assert orig == roundtrip1
```

## Values

For values, serializers are provided for:

* Decimal - serializes to a float.
* datetime - serializes to ISO8601.
* timedelta - serializes to a duration.

```python
from datetime import datetime, timedelta
from decimal import Decimal
from typing import TypedDict
from zoneinfo import ZoneInfo

from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
)


class ValueExample(TypedDict):
    distance: Decimal
    timestamp: datetime
    delay: timedelta


london = ZoneInfo('Europe/London')

orig: ValueExample = {
    'distance': Decimal('1234.5'),
    'timestamp': datetime(2024, 6, 1, 12, 0, 0, tzinfo=london),
    'delay': timedelta(hours=1, minutes=30),
}

text = serialize_typed(orig, ValueExample)
assert text == '{"distance": 1234.5, "timestamp": "2024-06-01T12:00:00.00+01:00", "delay": "PT1H30M"}'

roundtrip1 = deserialize_typed(text, ValueExample)
assert orig == roundtrip1
```
