# jetblack-serialization

Serialization for JSON and XML in Python using typing annotations
(read the [docs](https://rob-blackbourn.github.io/jetblack-serialization/)).

## Status

It has been tested with Python 3.7 used the `typing_extensions`
package for `TypedDict` and `Annotated`. In Python 3.8 the `TypedDict`
class is available in the standard `typing` package.

## Installation

The package can be installed with pip.

```bash
pip install jetblack-serialization
```

## Overview

The package adds support for type annotations when serializing or deserializing
JSON or XML.


### JSON

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

#### Serializing

This could be serialized to JSON as:

```python
from stringcase import camelcase, snakecase
from jetblack_serialize import SerializerConfig
from jetblack_serialize.json import serialize

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

#### Deserializing

We can deserialize the data as follows:

```python
from stringcase import camelcase, snakecase
from jetblack_serialize import SerializerConfig
from jetblack_serialize.json import deserialize

dct = deserialize(
    text,
    Annotated[Book, JSONValue()],
    SerializerConfig(camelcase, snakecase)
)
```

### XML

The XML version of the typed dictionary might look like this:

```python
from datetime import datetime
from typing import List, Optional, TypedDict, Union
from typing_extensions import Annotated
from jetblack_serialization import XMLEntity, XMLAttribute

class Book(TypedDict, total=False):
    book_id: Annotated[int, XMLAttribute("bookId")]
    title: str
    author: str
    publication_date: datetime
    keywords: Annotated[List[Annotated[str, XMLEntity("Keyword")]], XMLEntity("Keywords")]
    phrases: List[str]
    age: Optional[Union[datetime, int]]
    pages: Optional[int]
```

Note we have introduced some annotations to control the serialization.
For XML we have used pascal-case to serialized the keys and snake-case
for deserialization.

#### Serializing

To serialize we need to provide the containing tag `Book`:

```python
from stringcase import pascalcase, snakecase
from jetblack_serialize import SerializerConfig
from jetblack_serialize.xml import serialize

book: Book = {
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
    'pages': None
}
text = serialize(
    book,
    Annotated[Book, XMLEntity("Book")],
    SerializerConfig(pascalcase, snakecase)
)
print(text)
```

Producing:

```xml
<Book bookId="42">
    <Title>Little Red Book</Title>
    <Author>Chairman Mao</Author>
    <PublicationDate>1973-01-01T21:52:13.00Z</PublicationDate>
    <Keywords>
        <Keyword>Revolution</Keyword>
        <Keyword>Communism</Keyword>
    </Keywords>
    <Phrase>Revolutionary wars are inevitable in class society</Phrase>
    <Phrase>War is the continuation of politics</Phrase>
    <Age>24</Age>
</Book>'
```

The annotations are more elaborate here. However, much of the typed dictionary
requires no annotation.

First we needed the outer document wrapper `XMLEntity("Book")`.

Next we annotated the `book_id` to be an `XMLAttribute`.

Finally we annotated the two lists differently. The `keywords` list used
a nested structure, which we indicated by giving the list a different
`XMLEntity` tag to the list items. For the phrases we used the default
in-line behaviour.

#### Deserializing

We can deserialize the XML as follows:

```python
from stringcase import pascalcase, snakecase
from jetblack_serialize import SerializerConfig
from jetblack_serialize.xml import deserialize

dct = deserialize(
    text,
    Annotated[Book, XMLEntity("Book")],
    SerializerConfig(pascalcase, snakecase)
)
```

## Attributes

For JSON, attributes are typically not required. However
`JSONProperty(tag: str)` and `JSONValue()` are provided for
completeness.