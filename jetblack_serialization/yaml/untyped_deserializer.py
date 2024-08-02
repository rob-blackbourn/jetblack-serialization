"""Untyped YAML deserialization"""

from typing import Any, AnyStr

import yaml

from ..json.untyped_deserializer import from_untyped_object

from .config import SerializerConfig


def deserialize_untyped(
        text: AnyStr,
        config: SerializerConfig,
) -> Any:
    obj = yaml.load(text, Loader=config.loader)
    return from_untyped_object(obj, config)
