"""JSON Serialization"""

from .annotations import JSONValue, JSONProperty
from .config import SerializerConfig
from .serialization import (
    serialize,
    deserialize
)
from .typed_serializer import serialize_typed
from .typed_deserializer import (
    from_json_value,
    deserialize_typed
)
from .untyped_serializer import serialize_untyped
from .untyped_deserializer import deserialize_untyped

__all__ = [
    'JSONValue',
    'JSONProperty',

    'SerializerConfig',

    'serialize',
    'deserialize',
    'from_json_value',
    'serialize_typed',
    'deserialize_typed',
    'serialize_untyped',
    'deserialize_untyped',
]
