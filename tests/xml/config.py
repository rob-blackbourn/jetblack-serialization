"""Configuration"""

from datetime import datetime
from enum import Enum, auto
from typing import List, Optional, TypedDict, Union

from stringcase import pascalcase, snakecase
from typing_extensions import Annotated

from jetblack_serialization import SerializerConfig
from jetblack_serialization.xml import (
    XMLEntity,
    XMLAttribute,
)

CONFIG = SerializerConfig(
    key_serializer=pascalcase,
    key_deserializer=snakecase,
)


class Genre(Enum):
    POLITICAL = auto()
    HORROR = auto()
    ROMANTIC = auto()


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
    genre: Annotated[
        Genre,
        XMLEntity("Genre")
    ]
