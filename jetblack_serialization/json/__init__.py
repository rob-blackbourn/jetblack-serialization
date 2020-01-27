"""JSON Serialization"""

from .annotations import JSONValue, JSONProperty
from .typed_deserializer import (
    from_json_value
)
from .serialization import (
    serialize,
    deserialize
)

__all__ = [
    'JSONValue',
    'JSONProperty',

    'serialize',
    'deserialize',
    'from_json_value'
]
