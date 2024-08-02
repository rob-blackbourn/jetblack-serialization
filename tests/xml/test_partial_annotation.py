"""Test for the XML serializer"""

from datetime import datetime
from typing import List, Optional, TypedDict, Union

from stringcase import pascalcase, snakecase
from typing_extensions import Annotated

from jetblack_serialization.config import SerializerConfig
from jetblack_serialization.xml import (
    XMLEntity,
    XMLAttribute,
    serialize
)

CONFIG = SerializerConfig(serialize_key=pascalcase, deserialize_key=snakecase)


class Book(TypedDict, total=False):
    book_id: Annotated[
        int,
        XMLAttribute("bookId")
    ]
    title: str
    author: str
    publication_date: datetime
    keywords: Annotated[
        List[Annotated[str, XMLEntity("Keyword")]],
        XMLEntity("Keywords")
    ]
    phrases: Annotated[
        List[Annotated[str, XMLEntity("Phrase")]],
        XMLEntity("Phrase")
    ]
    age: Optional[Union[datetime, int]]
    pages: Optional[int]


def test_serialize() -> None:
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
    text = serialize(book, Annotated[Book, XMLEntity("Book")], CONFIG)
    assert text == '<Book bookId="42"><Title>Little Red Book</Title><Author>Chairman Mao</Author><PublicationDate>1973-01-01T21:52:13.00Z</PublicationDate><Keywords><Keyword>Revolution</Keyword><Keyword>Communism</Keyword></Keywords><Phrase>Revolutionary wars are inevitable in class society</Phrase><Phrase>War is the continuation of politics</Phrase><Age>24</Age><Pages/></Book>'
