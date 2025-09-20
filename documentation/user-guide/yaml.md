# Serializing YAML

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

This could be serialized to YAML as:

```python
from stringcase import camelcase, snakecase
from jetblack_serialization.yaml import serialize, SerializerConfig

text = serialize(
    obj,
    Book,
    SerializerConfig(key_serializer=camelcase, pretty_print=True)
)
print(text)
```

giving:

```yaml
bookId: 42
title: Little Red Book
author: Chairman Mao
publicationDate: '1973-01-01T21:52:13.00Z'
keywords:
- Revolution
- Communism
phrases:
- Revolutionary wars are inevitable in class society
- War is the continuation of politics
age: 24
pages: null
```

Note the fields have been camel cased, and the publication date has been turned
into an ISO 8601 date.

## Deserializing

We can deserialize the data as follows:

```python
from stringcase import snakecase
from jetblack_serialization.yaml import deserialize, SerializerConfig

dct = deserialize(
    text,
    Annotated[Book, YAMLValue()],
    SerializerConfig(key_deserializer=snakecase)
)
```

## Attributes

For YAML, attributes are typically not required. However
`YAMLProperty`, `YAMLObject` and `YAMLValue` which are simply
synonyms of the JSON attributes.
