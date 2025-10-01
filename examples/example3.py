import csv
from io import StringIO
from typing import Any, TypedDict

from jetblack_serialization.csv.typed_serializer import serialize_typed
from jetblack_serialization.config import DEFAULT_CONFIG


class Address(TypedDict):
    street: str
    city: str
    zip_code: str


class Person(TypedDict):
    name: str
    age: int
    address: Address


def make_paths(annotation: Any) -> None:
    pass


def main() -> None:
    people: list[Person] = [
        {
            "name": "Alice",
            "age": 30,
            "address": {
                "street": "123 Maple St",
                "city": "Springfield",
                "zip_code": "12345"
            },
        },
        {
            "name": "Bob",
            "age": 25,
            "address": {
                "street": "789 Pine St",
                "city": "Ogdenville",
                "zip_code": "54321"
            },
        }
    ]

    text = serialize_typed(people, list[Person], DEFAULT_CONFIG)
    print(text)

    # fp = StringIO()
    # writer = csv.writer(fp)
    # for person in people:
    #     writer.writerow(person)
    # text = fp.getvalue()
    # print(text)


if __name__ == "__main__":
    main()
