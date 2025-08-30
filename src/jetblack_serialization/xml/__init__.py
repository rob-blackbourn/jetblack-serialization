"""XML Serialization"""

from .annotations import (
    XMLAttribute,
    XMLEntity
)
from .serialization import serialize, deserialize
from .typed_serializer import serialize_typed
from .typed_deserializer import deserialize_typed
from .untyped_serializer import serialize_untyped
from .untyped_deserializer import deserialize_untyped

__all__ = [
    'XMLAttribute',
    'XMLEntity',

    'serialize',
    'deserialize',

    'serialize_typed',
    'deserialize_typed',

    'serialize_untyped',
    'deserialize_untyped',
]
