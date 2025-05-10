"""XML configuration"""

from typing import Callable, Optional, Type, Union

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
        key_serializer: Optional[Callable[[str], str]] = None,
        key_deserializer: Optional[Callable[[str], str]] = None,
        value_serializers: ValueSerializers = VALUE_SERIALIZERS,
        value_deserializers: ValueDeserializers = VALUE_DESERIALIZERS,
        loader: Optional[Type[_Loader]] = None,
        dumper: Optional[Type[_Dumper]] = None
    ) -> None:
        super().__init__(
            key_serializer,
            key_deserializer,
            value_serializers,
            value_deserializers
        )
        self.loader = loader or yaml.SafeLoader
        self.dumper = dumper or yaml.SafeDumper
