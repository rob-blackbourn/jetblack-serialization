"""XML configuration"""

from typing import Callable

from ..config import (
    BaseSerializerConfig,
    VALUE_DESERIALIZERS,
    VALUE_SERIALIZERS,
    ValueDeserializers,
    ValueSerializers
)


class SerializerConfig(BaseSerializerConfig):

    def __init__(
        self,
        *,
        key_serializer: Callable[[str], str] | None = None,
        key_deserializer: Callable[[str], str] | None = None,
        value_serializers: ValueSerializers = VALUE_SERIALIZERS,
        value_deserializers: ValueDeserializers = VALUE_DESERIALIZERS,
        pretty_print: bool = False
    ) -> None:
        super().__init__(
            key_serializer,
            key_deserializer,
            value_serializers,
            value_deserializers
        )
        self.pretty_print = pretty_print
