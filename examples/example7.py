from typing import Annotated, Any, Literal, TypedDict

from jetblack_serialization import Annotation
from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
    JSONValue,
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


def main() -> None:
    example = ShapeCircle(name='henry', type='circle', radius=1.0)
    text = serialize_typed(example, ShapeCircle)

    print(example)

    roundtrip1 = deserialize_typed(
        text,
        ShapeCircle | ShapeRectangle,
    )
    print(roundtrip1)

    roundtrip2 = deserialize_typed(
        text,
        Annotated[
            ShapeCircle | ShapeRectangle,
            JSONValue(type_selector=select_shape_type)
        ]
    )
    print(roundtrip2)

    print("here")


if __name__ == "__main__":
    main()
