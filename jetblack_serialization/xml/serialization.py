"""Helpers"""

from typing import Any

from ..types import (
    Annotation,
    MediaType,
    MediaTypeParams
)
from ..config import SerializerConfig
from .deserializer import deserialize
from .serializer import serialize


def from_xml(
        _media_type: MediaType,
        _params: MediaTypeParams,
        config: SerializerConfig,
        text: str,
        annotation: Annotation
) -> Any:
    return deserialize(text, annotation, config)


def to_xml(
        _media_type: MediaType,
        _params: MediaTypeParams,
        config: SerializerConfig,
        obj: Any,
        annotation: Any,
) -> str:
    return serialize(obj, annotation, config)
