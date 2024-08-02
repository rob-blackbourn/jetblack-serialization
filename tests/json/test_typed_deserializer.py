"""Tests for JSON serialization"""

from datetime import datetime
from typing import List, Optional, TypedDict, Union

from typing_extensions import Annotated

from jetblack_serialization.json import (
    JSONValue,
    JSONProperty,
    deserialize_typed
)
from jetblack_serialization.custom_annotations import DefaultValue

from .config import Genre, Image, CONFIG


TEXT = """
{
    "bookId": 42,
    "title": "Little Red Book",
    "author": "Chairman Mao",
    "publicationDate": "1973-01-01T21:52:13Z",
    "keywords": [
      "Revolution",
      "Communism"
    ],
    "phrases": [
        "Revolutionary wars are inevitable in class society",
        "War is the continuation of politics"
    ],
    "age": 24,
    "genre": "POLITICAL",
    "cover": "red-star.png"
}
"""

DICT = {
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
    'pages': None,
    "genre": Genre.POLITICAL,
    "cover": Image("red-star.png")
}


class AnnotatedBook(TypedDict):
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
    age: Optional[Union[datetime, int]]
    pages: Annotated[Optional[int], DefaultValue(None)]
    genre: Annotated[Genre, JSONProperty('genre')]
    cover: Annotated[Image, JSONProperty('cover')]


def test_deserialize_json_annotated() -> None:
    """Test for deserialize"""

    dct = deserialize_typed(
        TEXT,
        Annotated[AnnotatedBook, JSONValue()],
        CONFIG
    )
    assert dct == DICT


class Book(TypedDict):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: List[str]
    phrases: List[str]
    age: Optional[Union[datetime, int]]
    pages: Annotated[Optional[int], DefaultValue(None)]
    genre: Genre
    cover: Image


def test_deserialize_json_unannotated() -> None:
    """Test for deserialize"""

    dct = deserialize_typed(
        TEXT,
        Book,
        CONFIG
    )
    assert dct == DICT
