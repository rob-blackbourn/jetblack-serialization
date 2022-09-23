# Serializing JSON

Given a typed dictionary:

```python
from datetime import datetime
from typing import List, Optional, TypedDict, Union

class Book(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: List[str]
    phrases: List[str]
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
from jetblack_serialization import SerializerConfig
from jetblack_serialization.json import serialize

text = serialize(
    obj,
    Book,
    SerializerConfig(camelcase, snakecase, pretty_print=True)
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
from jetblack_serialization import SerializerConfig
from jetblack_serialization.json import deserialize

dct = deserialize(
    text,
    Annotated[Book, JSONValue()],
    SerializerConfig(camelcase, snakecase)
)
```

## Attributes

For JSON, attributes are typically not required. However
`JSONProperty(tag: str)` and `JSONValue()` are provided for
completeness.