"""Serializer Config"""

from typing import Callable, Optional


def _same_name(name: str) -> str:
    return name


class SerializerConfig:
    """Configuration for serialization"""

    def __init__(
        self,
        serialize_key: Optional[Callable[[str], str]],
        deserialize_key: Optional[Callable[[str], str]],
        *,
        pretty_print: bool = False
    ) -> None:
        self.serialize_key = serialize_key or _same_name
        self.deserialize_key = deserialize_key or _same_name
        self.pretty_print = pretty_print
