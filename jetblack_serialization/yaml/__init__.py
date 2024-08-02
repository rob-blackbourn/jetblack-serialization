"""YAML Serialization"""

from ..json import (
    JSONProperty as YAMLProperty,
    JSONValue as YAMLValue
)
from .config import YAMLSerializerConfig
from .serialization import serialize, deserialize
from .typed_serializer import serialize_typed
from .typed_deserializer import deserialize_typed
from .untyped_serializer import serialize_untyped
from .untyped_deserializer import deserialize_untyped

__all__ = [
    'serialize',
    'deserialize',

    'YAMLSerializerConfig',

    'serialize_typed',
    'deserialize_typed',

    'serialize_untyped',
    'deserialize_untyped',
]
