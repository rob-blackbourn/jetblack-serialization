"""Test for the XML serializer"""

from datetime import datetime
from typing import List, Optional, Union

from stringcase import pascalcase, snakecase

try:
    from typing import TypedDict  # type:ignore
except:  # pylint: disable=bare-except
    from typing_extensions import TypedDict

from typing_extensions import Annotated  # type: ignore

from jetblack_serialization.config import SerializerConfig
from jetblack_serialization.xml.typed_serializer import serialize_typed
from jetblack_serialization.xml.annotations import (
    XMLEntity,
    XMLAttribute
)

CONFIG = SerializerConfig(pascalcase, snakecase)


class Book(TypedDict, total=False):
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


def test_xml_serialize_typed():
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
    text = serialize_typed(book, Annotated[Book, XMLEntity("Book")], CONFIG)
    assert text == '<Book bookId="42"><Title>Little Red Book</Title><Author>Chairman Mao</Author><PublicationDate>1973-01-01T21:52:13.00Z</PublicationDate><Keywords><Keyword>Revolution</Keyword><Keyword>Communism</Keyword></Keywords><Phrase>Revolutionary wars are inevitable in class society</Phrase><Phrase>War is the continuation of politics</Phrase><Age>24</Age><pages/></Book>'

