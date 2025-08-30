from typing import Any, Callable

import yaml

type YAMLEncoder = Callable[[Any], str]
type YAMLDecoder = Callable[[str | bytes | bytearray], Any]


def ENCODE_YAML(obj: Any) -> str:
    return yaml.safe_dump(obj)


def DECODE_YAML(text: str | bytes | bytearray) -> Any:
    return yaml.safe_load(text)
