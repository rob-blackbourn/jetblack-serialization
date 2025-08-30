from typing import TypedDict

from jetblack_serialization.json import serialize_typed, deserialize_typed


class Foo(TypedDict):
    x: int


class Example(TypedDict, total=False):
    a: dict[str, Foo]


def main() -> None:
    example = Example(a={'one': {'x': 1}, 'two': {'x': 2}})
    text = serialize_typed(example, Example)
    roundtrip = deserialize_typed(text, Example)
    print(example)
    print(roundtrip)

    print("here")


if __name__ == "__main__":
    main()
