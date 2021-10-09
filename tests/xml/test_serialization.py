"""Round trip tests for XML serialization"""

from datetime import datetime
from typing import Any, List, Optional, Union

from stringcase import pascalcase, snakecase

try:
    from typing import TypedDict  # type:ignore
except:  # pylint: disable=bare-except
    from typing_extensions import TypedDict

from typing_extensions import Annotated  # type: ignore

from jetblack_serialization.config import SerializerConfig
from jetblack_serialization.xml.serializer import serialize
from jetblack_serialization.xml.deserializer import deserialize
from jetblack_serialization.xml.annotations import (
    XMLEntity,
    XMLAttribute
)

CONFIG = SerializerConfig(pascalcase, snakecase)


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


def test_typed():
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
    config = SerializerConfig(pascalcase, snakecase)

    text = serialize(dct, annotation, config)
    roundtrip = deserialize(text, annotation, config)
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


def test_untyped():
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
    config = SerializerConfig(pascalcase, snakecase)

    text = serialize(dct, annotation, config)
    roundtrip = deserialize(text, annotation, config)
    assert dct == roundtrip

def test_untyped_unannotated():
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
    annotation = Annotated[UnannotatedBook, Any]
    config = SerializerConfig(pascalcase, snakecase)

    text = serialize(dct, annotation, config)
    roundtrip = deserialize(text, annotation, config)
    assert dct == roundtrip
