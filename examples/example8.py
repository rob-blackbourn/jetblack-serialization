from typing import Annotated, Any, Literal, TypedDict

from jetblack_serialization import Annotation
from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
    JSONValue
)


class ShapeBase(TypedDict):
    name: str
    type: Literal['circle', 'rectangle']


class ShapeCircle(ShapeBase):
    radius: float


class ShapeRectangle(ShapeBase):
    width: float
    height: float


def select_shape_type(data: Any, _annotation: Annotation) -> Annotation:
    assert isinstance(data, dict)
    match data.get('type'):
        case 'circle':
            return ShapeCircle
        case 'rectangle':
            return ShapeRectangle
        case _:
            raise ValueError(f"Unknown shape type: {data.get('type')}")


class Button(TypedDict):
    title: str
    shape: Annotated[
        ShapeCircle | ShapeRectangle,
        JSONValue(type_selector=select_shape_type)
    ]


def main() -> None:
    example: Button = {
        'title': "press",
        'shape': {
            'radius': 1.0,
            'name': 'henry',
            'type': 'circle'
        }
    }
    text = serialize_typed(example, Button)

    print(example)

    roundtrip = deserialize_typed(text, Button)
    print(roundtrip)

    print("here")


if __name__ == "__main__":
    main()
