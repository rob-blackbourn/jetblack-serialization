"""JSON configuration"""

from typing import Callable

from ..config import (
    BaseSerializerConfig,
    VALUE_DESERIALIZERS,
    VALUE_SERIALIZERS,
    ValueDeserializers,
    ValueSerializers,
    ToObject,
    FromObject
)


class SerializerConfig(BaseSerializerConfig):

    def __init__(
        self,
        *,
        key_serializer: Callable[[str], str] | None = None,
        key_deserializer: Callable[[str], str] | None = None,
        value_serializers: ValueSerializers = VALUE_SERIALIZERS,
        value_deserializers: ValueDeserializers = VALUE_DESERIALIZERS,
        to_object: ToObject | None = None,
        from_object: FromObject | None = None,
    ) -> None:
        super().__init__(
            key_serializer,
            key_deserializer,
            value_serializers,
            value_deserializers
        )
        self.to_object = to_object
        self.from_object = from_object
