"""Typed YAML deserialization"""

from typing import Any, Union

import yaml

from ..json import from_json_value
from ..types import Annotation

from .config import SerializerConfig


def deserialize_typed(
        text: Union[str, bytes, bytearray],
        annotation: Annotation,
        config: SerializerConfig
) -> Any:
    """Convert YAML to an object.

    Args:
        text (Union[str, bytes, bytearray]): The YAML string
        annotation (str): The type annotation.
        config (YAMLSerializationConfig): The YAML config.

    Returns:
        Any: The deserialized object.
    """
    json_value = yaml.load(text, Loader=config.loader)
    return from_json_value(config, json_value, annotation)
