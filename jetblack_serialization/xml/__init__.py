"""XML Serialization"""

from .annotations import (
    XMLAttribute,
    XMLEntity
)

from .deserializer import deserialize
from .serializer import serialize

__all__ = [
    'XMLAttribute',
    'XMLEntity',

    'deserialize',
    'serialize'
]
