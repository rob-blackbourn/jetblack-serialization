"""Tests for JSON serialization"""

from datetime import datetime
from typing import List, Optional, Union

from stringcase import snakecase, camelcase

from typing_extensions import TypedDict, Annotated  # type: ignore

from jetblack_serialization.config import SerializerConfig
from jetblack_serialization.json.typed_deserializer import deserialize
from jetblack_serialization.json.annotations import (
    JSONValue,
    JSONProperty
)

CONFIG = SerializerConfig(camelcase, snakecase)


class Book(TypedDict, total=False):
    book_id: Annotated[int, JSONProperty("bookId")]
    title: Annotated[str, JSONProperty("title")]
    author: Annotated[str, JSONProperty("author")]
    publication_date: Annotated[datetime, JSONProperty("publicationDate")]
    keywords: Annotated[List[Annotated[str, JSONValue()]],
                        JSONProperty("keywords")]
    phrases: Annotated[List[Annotated[str, JSONValue()]],
                       JSONProperty("phrases")]
    age: Annotated[Optional[Union[datetime, int]], JSONProperty("age")]
    pages: Annotated[Optional[int], JSONProperty("pages")]


def test_deserialize():
    """Test for deserialize"""

    text = """
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
    "age": 24
}
"""
    dct = deserialize(
        text,
        Annotated[Book, JSONValue()],
        CONFIG
    )
    assert dct == {
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
