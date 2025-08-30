import json
from typing import Any, Callable

type JSONEncoder = Callable[[Any], str]
type JSONDecoder = Callable[[str | bytes | bytearray], Any]


def ENCODE_JSON(obj: Any) -> str:
    return json.dumps(obj)


def DECODE_JSON(text: str | bytes | bytearray) -> Any:
    return json.loads(text)
