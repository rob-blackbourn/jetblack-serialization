# Serializing JSON

Given a typed dictionary:

```python
from datetime import datetime
from typing import Optional, TypedDict, Union

class Book(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: list[str]
    phrases: list[str]
    age: Optional[Union[datetime, int]]
    pages: Optional[int]
```

Create some data:

```python
obj: Book = {
    'author': 'Chairman Mao',
    'book_id': 42,
    'title': 'Little Red Book',
    'publication_date': datetime(1973, 1, 1, 21, 52, 13),
    'keywords': ['Revolution', 'Communism'],
    'phrases': [
        'Revolutionary wars are inevitable in class society',
        'War is the continuation of politics'
    ],
    'age': 24,
}
```

## Serializing

This could be serialized to JSON as:

```python
from stringcase import camelcase, snakecase
from jetblack_serialization.json import serialize, SerializerConfig

text = serialize(
    obj,
    Book,
    SerializerConfig(key_serializer=camelcase, pretty_print=True)
)
print(text)
```

giving:

```json
{
    "bookId": 42,
    "title": "Little Red Book",
    "author": "Chairman Mao",
    "publicationDate": "1973-01-01T21:52:13.00Z",
    "keywords": ["Revolution", "Communism"],
    "phrases": ["Revolutionary wars are inevitable in class society", "War is the continuation of politics"],
    "age": 24,
    "pages": null
}
```

Note the fields have been camel cased, and the publication date has been turned
into an ISO 8601 date.

## Deserializing

We can deserialize the data as follows:

```python
from stringcase import camelcase, snakecase
from jetblack_serialization.json import deserialize, SerializerConfig

dct = deserialize(
    text,
    Annotated[Book, JSONValue()],
    SerializerConfig(key_deserializer=snakecase)
)
```

## Attributes

For JSON, attributes are typically not required. However
`JSONProperty`, `JSONObject` and `JSONValue()` are provided for
completeness.

### Resolving Unions With Type Selectors

The default behavior when handling a union is to attempt each element
and accept the first valid attempt. This is obviously inefficient, and
potentially inaccurate. We can use type selectors to sort this out.

Given the following schema:

```python
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
```

A type selector is given the data that is about to be serialized
(or deserialized), the type annotation, a boolean flag
indicating whether the value is being serialized or deserialized,
and the serializer config.

In the example below we use the 'shape_type' property to return the appropriate type.

```python
def select_shape_type(
        data: Any,
        type_annotation: Annotation,
        is_serializing: bool,
        config: SerializerConfig
) -> Annotation:
    assert isinstance(data, dict)
    key = 'shape_type'
    tag = key if is_serializing else config.serialize_key(key)
    match data.get(tag):
        case 'circle':
            return ShapeCircle
        case 'rectangle':
            return ShapeRectangle
        case _:
            raise ValueError(f"Unknown shape type: {data.get(tag)}")
```

A type selector can be passed to any of the JSON annotations using the
`type_selector` keyword argument.

The example below uses `JSONValue`.

```python
class Button(TypedDict):
    title: str
    shape: Annotated[
        Shape,
        JSONValue(type_selector=select_shape_type)
    ]
```

### Problematic Tag Names

Sometimes a tag name is something that is awkward to handle
in python. This might be a keyword, or contain an unrepresentable
character. The `JSONProperty` annotation can be used to specify the tag.

```python
class Schema(TypedDict):
    ref: Annotated[str, JSONProperty("$ref")]
```

### Value Style Keys

Sometimes property names or keys are actually values. For example in
an HTTP messages the headers can be considered keys; however they
should not be converted between camel-case and snake-case, as their
values have meaning. The property `is_serializable_keys` is available
in `JSONProperty` and `JSONObject`.

```python
class HttpRequest(TypedDict):
    method: Literal['GET', 'POST']
    headers: Annotated[dict[str, Any], JSONObject(is_serializable_keys=False)]
```
