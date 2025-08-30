# jetblack-serialization

Serialization for JSON, YAML and XML in Python using type annotations
(read the [docs](https://rob-blackbourn.github.io/jetblack-serialization/)).

## Installation

This is a Python 3.12+ package.

The package can be installed with pip.

```bash
pip install jetblack-serialization
```

By default, the dependencies for YAML and XML are not installed.

To install the dependencies for XML
([`lxml`](https://lxml.de/)).

```bash
pip install jetblack-serialization[xml]
```

To install the dependencies for YAML ([`PyYAML`](https://github.com/yaml/pyyaml)).

```bash
pip install jetblack-serialization[yaml]
```

To install the dependencies for all.

```bash
pip install jetblack-serialization[xml,yaml]
```

## Overview

The package adds support for type annotations when serializing or deserializing
JSON, YAML or XML.

### JSON

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

#### Serializing JSON

This could be serialized to JSON as:

```python
from stringcase import camelcase
from jetblack_serialization.json import serialize, SerializerConfig

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

#### Deserializing JSON

We can deserialize the data as follows:

```python
from stringcase import snakecase
from jetblack_serialization.json import deserialize, SerializerConfig

dct = deserialize(
    text,
    Annotated[Book, JSONValue()],
    SerializerConfig(key_deserializer=snakecase)
)
```

### YAML

YAML is a superset of JSON, so for serialization things are very similar.

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

#### Serializing YAML

This could be serialized to YAML as:

```python
from stringcase import camelcase
from jetblack_serialization.yaml import serialize, SerializerConfig

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

#### Deserializing YAML

We can deserialize the data as follows:

```python
from stringcase import snakecase
from jetblack_serialization.yaml import deserialize, SerializerConfig

dct = deserialize(
    text,
    Annotated[Book, JSONValue()],
    SerializerConfig(key_deserializer=snakecase)
)
```

### XML

The XML version of the typed dictionary might look like this:

```python
from datetime import datetime
from typing import Optional, TypedDict, Union
from typing_extensions import Annotated
from jetblack_serialization.xml import XMLEntity, XMLAttribute

class Book(TypedDict, total=False):
    book_id: Annotated[int, XMLAttribute("bookId")]
    title: str
    author: str
    publication_date: datetime
    keywords: Annotated[list[Annotated[str, XMLEntity("Keyword")]], XMLEntity("Keywords")]
    phrases: list[str]
    age: Optional[Union[datetime, int]]
    pages: Optional[int]
```

Note we have introduced some annotations to control the serialization.
For XML we have used pascal-case to serialized the keys and snake-case
for deserialization.

#### Serializing XML

To serialize we need to provide the containing tag `Book`:

```python
from stringcase import pascalcase
from jetblack_serialization.xml import serialize, SerializerConfig

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
    SerializerConfig(key_serializer=pascalcase)
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

#### Deserializing XML

We can deserialize the XML as follows:

```python
from stringcase import snakecase
from jetblack_serialization.xml import deserialize, SerializerConfig

dct = deserialize(
    text,
    Annotated[Book, XMLEntity("Book")],
    SerializerConfig(key_deserializer=snakecase)
)
```

## Attributes

For JSON, attributes are typically not required. However
`JSONProperty(tag: str)` and `JSONValue()` are provided for
completeness.

## Contributing

To run the tests with tox and pyenv:

```bash
VIRTUALENV_DISCOVERY=pyenv tox
```
