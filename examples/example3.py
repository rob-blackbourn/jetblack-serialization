import csv
from io import StringIO
from typing import Any, TypedDict


class Address(TypedDict):
    street: str
    city: str
    zip_code: str


class Person(TypedDict):
    name: str
    age: int
    addresses: list[Address]


def make_paths(annotation: Any) -> None:
    pass


def main() -> None:
    people: list[Person] = [
        {
            "name": "Alice",
            "age": 30,
            "addresses": [
                {"street": "123 Maple St", "city": "Springfield", "zip_code": "12345"},
                {"street": "456 Oak St", "city": "Shelbyville", "zip_code": "67890"},
            ],
        },
        {
            "name": "Bob",
            "age": 25,
            "addresses": [
                {"street": "789 Pine St", "city": "Ogdenville", "zip_code": "54321"},
                {"street": "101 Elm St", "city": "North Haverbrook", "zip_code": "98765"}
            ],
        }
    ]

    fp = StringIO()
    writer = csv.writer(fp)
    for person in people:
        writer.writerow(person)
    text = fp.getvalue()
    print(text)


if __name__ == "__main__":
    main()
