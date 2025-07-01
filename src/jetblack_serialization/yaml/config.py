"""XML configuration"""

from typing import Callable, Union

import yaml

from ..config import (
    BaseSerializerConfig,
    VALUE_DESERIALIZERS,
    VALUE_SERIALIZERS,
    ValueDeserializers,
    ValueSerializers
)


_Dumper = Union[
    yaml.BaseDumper,
    yaml.Dumper,
    yaml.SafeDumper
]
_Loader = Union[
    yaml.Loader,
    yaml.BaseLoader,
    yaml.FullLoader,
    yaml.SafeLoader,
    yaml.UnsafeLoader
]


class SerializerConfig(BaseSerializerConfig):

    def __init__(
        self,
        *,
        key_serializer: Callable[[str], str] | None = None,
        key_deserializer: Callable[[str], str] | None = None,
        value_serializers: ValueSerializers = VALUE_SERIALIZERS,
        value_deserializers: ValueDeserializers = VALUE_DESERIALIZERS,
        loader: type[_Loader] | None = None,
        dumper: type[_Dumper] | None = None
    ) -> None:
        super().__init__(
            key_serializer,
            key_deserializer,
            value_serializers,
            value_deserializers
        )
        self.loader = loader or yaml.SafeLoader
        self.dumper = dumper or yaml.SafeDumper
