"""Round trip tests for XML serialization"""

from datetime import datetime
from typing import List, Optional, TypedDict, Union

from stringcase import pascalcase, snakecase
from typing_extensions import Annotated

from jetblack_serialization.xml import (
    XMLEntity,
    XMLAttribute,
    XMLSerializerConfig,
    serialize,
    deserialize
)

CONFIG = XMLSerializerConfig(
    key_serializer=pascalcase,
    key_deserializer=snakecase
)


class AnnotatedBook(TypedDict, total=False):
    book_id: Annotated[
        int,
        XMLAttribute("bookId")
    ]
    title: Annotated[
        str,
        XMLEntity("Title")
    ]
    author: Annotated[
        str,
        XMLEntity("Author")
    ]
    publication_date: Annotated[
        datetime,
        XMLEntity("PublicationDate")
    ]
    keywords: Annotated[
        List[Annotated[str, XMLEntity("Keyword")]],
        XMLEntity("Keywords")
    ]
    phrases: Annotated[
        List[Annotated[str, XMLEntity("Phrase")]],
        XMLEntity("Phrase")
    ]
    age: Annotated[
        Optional[Union[datetime, int]],
        XMLEntity("Age")
    ]
    pages: Annotated[
        Optional[int],
        XMLAttribute("pages")
    ]


def test_xml_typed_annotated_roundtrip() -> None:
    dct: AnnotatedBook = {
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
    annotation = Annotated[AnnotatedBook, XMLEntity('Book')]

    text = serialize(dct, annotation, CONFIG)
    roundtrip = deserialize(text, annotation, CONFIG)
    assert dct == roundtrip


class UnannotatedBook(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: List[str]
    phrases: List[str]
    age: Optional[Union[datetime, int]]
    pages: Optional[int]


def test_xml_unannotated_roundtrip() -> None:
    dct: UnannotatedBook = {
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
    annotation = Annotated[UnannotatedBook, XMLEntity('Book')]

    text = serialize(dct, annotation, CONFIG)
    roundtrip = deserialize(text, annotation, CONFIG)
    assert dct == roundtrip


def test_xml_untyped_roundtrip() -> None:
    obj = {
        'int': 42,
        'str': 'a string',
        'list': [1, 2, 3],
        'dict': {
            'one': 1,
            'two': 2
        }
    }
    text = serialize(obj, None, CONFIG)
    roundtrip = deserialize(text, None, CONFIG)
    assert obj == roundtrip
