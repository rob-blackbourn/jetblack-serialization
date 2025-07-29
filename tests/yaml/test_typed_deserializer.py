"""Tests for YAML serialization"""

from datetime import datetime, timezone
from typing import Optional, TypedDict, Union

from typing_extensions import Annotated

from jetblack_serialization import DefaultValue
from jetblack_serialization.yaml import (
    YAMLValue,
    YAMLProperty,
    deserialize_typed
)

from .config import Genre, Image, CONFIG


TEXT = """
bookId: 42
title: Little Red Book
author: Chairman Mao
publicationDate: 1973-01-01T21:52:13Z
keywords:
- Revolution
- Communism
phrases:
- Revolutionary wars are inevitable in class society
- War is the continuation of politics
age: 24
genre: POLITICAL
cover: red-star.png
"""

DICT = {
    'author': 'Chairman Mao',
    'book_id': 42,
    'title': 'Little Red Book',
    'publication_date': datetime(1973, 1, 1, 21, 52, 13, tzinfo=timezone.utc),
    'keywords': ['Revolution', 'Communism'],
    'phrases': [
        'Revolutionary wars are inevitable in class society',
        'War is the continuation of politics'
    ],
    'age': 24,
    'pages': None,
    "genre": Genre.POLITICAL,
    "cover": Image("red-star.png")
}


class AnnotatedBook(TypedDict):
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
    age: Optional[Union[datetime, int]]
    pages: Annotated[Optional[int], DefaultValue(None)]
    genre: Annotated[Genre, YAMLProperty('genre')]
    cover: Annotated[Image, YAMLProperty('cover')]


def test_deserialize_yaml_annotated() -> None:
    """Test for deserialize"""

    dct = deserialize_typed(
        TEXT,
        Annotated[AnnotatedBook, YAMLValue()],
        CONFIG
    )
    assert dct == DICT


class Book(TypedDict):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: list[str]
    phrases: list[str]
    age: Optional[Union[datetime, int]]
    pages: Annotated[Optional[int], DefaultValue(None)]
    genre: Genre
    cover: Image


def test_deserialize_yaml_unannotated() -> None:
    """Test for deserialize"""

    dct = deserialize_typed(
        TEXT,
        Book,
        CONFIG
    )
    assert dct == DICT
