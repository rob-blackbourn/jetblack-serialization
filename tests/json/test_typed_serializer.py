"""Tests for JSON serialization"""

from datetime import datetime
from typing import List, Optional, TypedDict, Union

from typing_extensions import Annotated

from jetblack_serialization.json import (
    JSONValue,
    JSONProperty,
    serialize_typed
)

from .config import Genre, Image, CONFIG


class AnnotatedBook(TypedDict, total=False):
    book_id: Annotated[
        int,
        JSONProperty("bookId")
    ]
    title: Annotated[
        str,
        JSONProperty("title")
    ]
    author: Annotated[
        str,
        JSONProperty("author")
    ]
    publication_date: Annotated[
        datetime,
        JSONProperty("publicationDate")
    ]
    keywords: Annotated[
        List[Annotated[str, JSONValue()]],
        JSONProperty("keywords")
    ]
    phrases: Annotated[
        List[Annotated[str, JSONValue()]],
        JSONProperty("phrases")
    ]
    age: Annotated[
        Optional[Union[datetime, int]],
        JSONProperty("age")
    ]
    pages: Annotated[
        Optional[int],
        JSONProperty("pages")
    ]
    genre: Annotated[
        Genre,
        JSONProperty('genre')
    ]
    cover: Annotated[
        Image,
        JSONProperty('cover')
    ]


def test_json_serializer_annotated() -> None:
    """Test for deserializing a typed dict with JSON annotations"""

    obj: AnnotatedBook = {
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
        'genre': Genre.POLITICAL,
        'cover': Image('red-star.png')
    }
    text = serialize_typed(obj, AnnotatedBook, CONFIG)
    assert text == '{"bookId": 42, "title": "Little Red Book", "author": "Chairman Mao", "publicationDate": "1973-01-01T21:52:13.00Z", "keywords": ["Revolution", "Communism"], "phrases": ["Revolutionary wars are inevitable in class society", "War is the continuation of politics"], "age": 24, "genre": "POLITICAL", "cover": "red-star.png"}'


class UnannotatedBook(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: List[str]
    phrases: List[str]
    age: Optional[Union[datetime, int]]
    pages: Optional[int]
    genre: Genre
    cover: Image


def test_jason_serializer_unannotated() -> None:
    """Test for deserializing a typed dict without JSON annotations"""

    obj: UnannotatedBook = {
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
        'genre': Genre.POLITICAL,
        'cover': Image('red-star.png')
    }
    text = serialize_typed(
        obj,
        UnannotatedBook,
        CONFIG
    )
    assert text == '{"bookId": 42, "title": "Little Red Book", "author": "Chairman Mao", "publicationDate": "1973-01-01T21:52:13.00Z", "keywords": ["Revolution", "Communism"], "phrases": ["Revolutionary wars are inevitable in class society", "War is the continuation of politics"], "age": 24, "genre": "POLITICAL", "cover": "red-star.png"}'
