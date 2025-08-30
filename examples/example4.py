from datetime import datetime
from typing import Annotated, NotRequired, TypedDict

from jetblack_serialization import DefaultValue, DefaultFactory
from jetblack_serialization.json import serialize_typed, deserialize_typed


class Example(TypedDict, total=False):
    a: int
    b: NotRequired[Annotated[str, DefaultValue("default")]]
    c: Annotated[datetime, DefaultFactory(datetime.now)]


def main() -> None:
    example = Example(a=1)
    text = serialize_typed(example, Example)
    roundtrip = deserialize_typed(text, Example)
    print(example)
    print(roundtrip)

    print("here")


if __name__ == "__main__":
    main()
