"""XML Serialization"""

from .annotations import (
    XMLAttribute,
    XMLEntity
)

from .serialization import serialize, deserialize

__all__ = [
    'XMLAttribute',
    'XMLEntity',

    'deserialize',
    'serialize'
]
