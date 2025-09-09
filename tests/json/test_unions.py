from typing import Annotated, Any, Literal, TypedDict

from stringcase import snakecase, camelcase

from jetblack_serialization import Annotation, SerializerConfig
from jetblack_serialization.json import (
    serialize_typed,
    deserialize_typed,
    JSONValue,
)

CONFIG = SerializerConfig(
    key_serializer=camelcase,
    key_deserializer=snakecase,
)


class ShapeBase(TypedDict):
    name: str
    shape_type: Literal['circle', 'rectangle']


class ShapeCircle(ShapeBase):
    radius: float


class ShapeRectangle(ShapeBase):
    width: float
    height: float


type Shape = ShapeCircle | ShapeRectangle


def select_shape_type(data: Any, _annotation: Annotation) -> Annotation:
    assert isinstance(data, dict)
    match data.get('shape_type'):
        case 'circle':
            return ShapeCircle
        case 'rectangle':
            return ShapeRectangle
        case _:
            raise ValueError(f"Unknown shape type: {data.get('type')}")


def test_union() -> None:
    actual = ShapeCircle(name='henry', shape_type='circle', radius=1.0)
    text = serialize_typed(actual, ShapeCircle)

    roundtrip1 = deserialize_typed(
        text,
        ShapeCircle | ShapeRectangle,
    )
    assert actual == roundtrip1

    roundtrip2 = deserialize_typed(
        text,
        Annotated[
            ShapeCircle | ShapeRectangle,
            JSONValue(type_selector=select_shape_type)
        ]
    )
    assert actual == roundtrip2


class Button(TypedDict):
    title: str
    shape: Annotated[
        Shape,
        JSONValue(type_selector=select_shape_type)
    ]


def test_nested_union() -> None:
    actual: Button = {
        'title': "press",
        'shape': {
            'name': 'henry',
            'shape_type': 'circle',
            'radius': 1.0,
        }
    }
    text = serialize_typed(actual, Button)
    roundtrip = deserialize_typed(text, Button)
    assert actual == roundtrip
