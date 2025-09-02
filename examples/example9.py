from typing import Any, TypedDict

from jetblack_serialization.json import serialize_typed, deserialize_typed


class Example(TypedDict):
    value: Any


def main() -> None:
    example1 = Example(value='foo')
    text1 = serialize_typed(example1, Example)
    roundtrip1 = deserialize_typed(text1, Example)
    assert example1 == roundtrip1
    print(example1)
    print(roundtrip1)

    example2 = Example(value=[1, 2, 3])
    text2 = serialize_typed(example2, Example)
    roundtrip2 = deserialize_typed(text2, Example)
    assert example2 == roundtrip2
    print(example2)
    print(roundtrip2)

    print("here")


if __name__ == "__main__":
    main()
