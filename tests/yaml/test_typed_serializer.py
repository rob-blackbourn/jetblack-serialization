"""Tests for JSON serialization"""

from datetime import datetime
from typing import Optional, TypedDict, Union

from typing_extensions import Annotated

from jetblack_serialization.yaml import (
    YAMLValue,
    YAMLProperty,
    serialize_typed
)

from .config import Genre, Image, CONFIG


class AnnotatedBook(TypedDict, total=False):
    book_id: Annotated[
        int,
        YAMLProperty("bookId")
    ]
    title: Annotated[
        str,
        YAMLProperty("title")
    ]
    author: Annotated[
        str,
        YAMLProperty("author")
    ]
    publication_date: Annotated[
        datetime,
        YAMLProperty("publicationDate")
    ]
    keywords: Annotated[
        list[Annotated[str, YAMLValue()]],
        YAMLProperty("keywords")
    ]
    phrases: Annotated[
        list[Annotated[str, YAMLValue()]],
        YAMLProperty("phrases")
    ]
    age: Annotated[
        Optional[Union[datetime, int]],
        YAMLProperty("age")
    ]
    pages: Annotated[
        Optional[int],
        YAMLProperty("pages")
    ]
    genre: Annotated[
        Genre,
        YAMLProperty('genre')
    ]
    cover: Annotated[
        Image,
        YAMLProperty('cover')
    ]


def test_yaml_serializer_annotated() -> None:
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
    actual = serialize_typed(obj, AnnotatedBook, CONFIG)

    expected = """age: 24
author: Chairman Mao
bookId: 42
cover: red-star.png
genre: POLITICAL
keywords:
- Revolution
- Communism
phrases:
- Revolutionary wars are inevitable in class society
- War is the continuation of politics
publicationDate: '1973-01-01T21:52:13.00Z'
title: Little Red Book
"""
    assert actual == expected


class UnannotatedBook(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: list[str]
    phrases: list[str]
    age: Optional[Union[datetime, int]]
    pages: Optional[int]
    genre: Genre
    cover: Image


def test_yaml_serializer_unannotated() -> None:
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
    actual = serialize_typed(
        obj,
        UnannotatedBook,
        CONFIG
    )
    expected = """age: 24
author: Chairman Mao
bookId: 42
cover: red-star.png
genre: POLITICAL
keywords:
- Revolution
- Communism
phrases:
- Revolutionary wars are inevitable in class society
- War is the continuation of politics
publicationDate: '1973-01-01T21:52:13.00Z'
title: Little Red Book
"""
    assert actual == expected
