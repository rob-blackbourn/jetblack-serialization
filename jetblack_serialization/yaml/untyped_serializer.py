"""Untyped YAML serialization"""

from typing import Any, Type

import yaml

from ..config import SerializerConfig
from ..json.untyped_serializer import from_untyped_object
from .types import _Dumper


def serialize_untyped(
        obj: Any,
        config: SerializerConfig,
        *,
        dumper: Type[_Dumper] = yaml.SafeDumper
) -> str:
    json_obj = from_untyped_object(obj, config)
    return yaml.dump(
        json_obj,
        Dumper=dumper
    )
