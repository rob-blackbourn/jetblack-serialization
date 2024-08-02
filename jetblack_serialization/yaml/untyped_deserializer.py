"""Untyped YAML deserialization"""

from typing import Any, AnyStr

import yaml

from ..json.untyped_deserializer import from_untyped_object

from .config import YAMLSerializerConfig


def deserialize_untyped(
        text: AnyStr,
        config: YAMLSerializerConfig,
) -> Any:
    obj = yaml.load(text, Loader=config.loader)
    return from_untyped_object(obj, config)
