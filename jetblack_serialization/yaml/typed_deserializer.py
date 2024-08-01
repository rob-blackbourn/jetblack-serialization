"""Typed YAML deserialization"""

from typing import Any, Type, Union

import yaml

from ..config import SerializerConfig
from ..json import from_json_value
from ..types import Annotation

_Loader = Union[
    yaml.Loader,
    yaml.BaseLoader,
    yaml.FullLoader,
    yaml.SafeLoader,
    yaml.UnsafeLoader
]


def deserialize_typed(
        text: Union[str, bytes, bytearray],
        annotation: Annotation,
        config: SerializerConfig,
        *,
        loader: Type[_Loader] = yaml.SafeLoader
) -> Any:
    """Convert YAML to an object.

    Args:
        text (Union[str, bytes, bytearray]): The YAML string
        annotation (str): The type annotation
        loader (Type[Loader | BaseLoader | FullLoader | SafeLoader | UnsafeLoader], optional): Optional
            loader. Defaults to `SafeLoader`.

    Returns:
        Any: The deserialized object.
    """
    json_value = yaml.load(text, Loader=loader)
    return from_json_value(config, json_value, annotation)
