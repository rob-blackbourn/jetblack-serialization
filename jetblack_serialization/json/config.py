"""JSON configuration"""

from typing import Callable, Optional

from ..config import (
    SerializerConfig,
    VALUE_DESERIALIZERS,
    VALUE_SERIALIZERS,
    ValueDeserializers,
    ValueSerializers
)


class JSONSerializerConfig(SerializerConfig):

    def __init__(
        self,
        *,
        key_serializer: Optional[Callable[[str], str]] = None,
        key_deserializer: Optional[Callable[[str], str]] = None,
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
