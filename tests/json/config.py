"""Utilities"""

from enum import Enum, auto
from typing import List, Self, Tuple, Type

from stringcase import snakecase, camelcase

from jetblack_serialization import (
    ValueSerializer,
    ValueDeserializer,
    VALUE_SERIALIZERS,
    VALUE_DESERIALIZERS,
)
from jetblack_serialization import SerializerConfig


class Genre(Enum):
    POLITICAL = auto()
    HORROR = auto()
    ROMANTIC = auto()


class Image:
    def __init__(self, value: str) -> None:
        self.value = value

    def __eq__(self, other) -> bool:
        return self.value == other.value

    @classmethod
    def to_image(cls, value: str) -> Self:
        return cls(value)

    def from_image(self) -> str:
        return self.value


value_serializers: List[Tuple[Type, ValueSerializer]] = [
    (Image, Image.from_image)
]
value_serializers += VALUE_SERIALIZERS

value_deserializers: List[Tuple[Type, ValueDeserializer]] = [
    (Image, Image.to_image)
]
value_deserializers += VALUE_DESERIALIZERS


CONFIG = SerializerConfig(
    key_serializer=camelcase,
    key_deserializer=snakecase,
    value_serializers=value_serializers,
    value_deserializers=value_deserializers
)
