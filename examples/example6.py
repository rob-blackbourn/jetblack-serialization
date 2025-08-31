from typing import Literal, TypedDict

from jetblack_serialization.json import serialize_typed, deserialize_typed


class Example(TypedDict):
    scheme: Literal['http', 'https', 'ws', 'wss']


def main() -> None:
    example = Example(scheme='http')
    text = serialize_typed(example, Example)
    roundtrip = deserialize_typed(text, Example)
    print(example)
    print(roundtrip)

    print("here")


if __name__ == "__main__":
    main()
