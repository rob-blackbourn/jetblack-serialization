"""XML Serialization"""

from .annotations import (
    XMLAttribute,
    XMLEntity
)

from .deserializer import deserialize
from .serializer import serialize
from .serialization import from_xml, to_xml

__all__ = [
    'XMLAttribute',
    'XMLEntity',
    'deserialize',
    'serialize',
    'from_xml',
    'to_xml'
]
