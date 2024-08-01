"""Untyped YAML deserialization"""

from typing import Any, AnyStr, Type

import yaml

from ..config import SerializerConfig
from ..json.untyped_deserializer import from_untyped_object

from .types import _Loader


def deserialize_untyped(
        text: AnyStr,
        config: SerializerConfig,
        *,
        loader: Type[_Loader] = yaml.SafeLoader
) -> Any:
    obj = yaml.load(text, Loader=loader)
    return from_untyped_object(obj, config)
