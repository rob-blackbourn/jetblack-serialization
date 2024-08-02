"""Untyped YAML serialization"""

from typing import Any

import yaml

from ..json.untyped_serializer import from_untyped_object

from .config import YAMLSerializerConfig


def serialize_untyped(
        obj: Any,
        config: YAMLSerializerConfig,
) -> str:
    json_obj = from_untyped_object(obj, config)
    return yaml.dump(
        json_obj,
        Dumper=config.dumper
    )
