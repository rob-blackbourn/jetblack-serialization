from typing import Any, Callable, Sequence

type CSVEncoder = Callable[[Sequence[Sequence[str]]], str]
type JSONDecoder = Callable[[str | bytes | bytearray], Sequence[Sequence[str]]]


def ENCODE_CSV(rows: Sequence[Sequence[str]]) -> str:
    return "\n".join(
        ",".join(row)
        for row in rows
    )


def DECODE_JSON(text: str | bytes | bytearray) -> Any:
    if isinstance(text, (bytes, bytearray)):
        text = text.decode('utf-8')
    return [
        [
            col
            for col in row.split('\n')
        ]
        for row in text.split('\n')
    ]
