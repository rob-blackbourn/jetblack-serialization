"""Tests for serialization"""

from datetime import datetime, UTC

from typing_extensions import Annotated

from jetblack_serialization.xml import XMLEntity, deserialize

from .config import CONFIG, Book, Genre


def test_xml_deserialize_annotated() -> None:
    """Test for from_xml_element"""

    text = """
<Book  bookId="42">
    <Title>Little Red Book</Title>
    <Author>Chairman Mao</Author>
    <PublicationDate>1973-01-01T21:52:13Z</PublicationDate>
    <Keywords>
      <Keyword>Revolution</Keyword>
      <Keyword>Communism</Keyword>
    </Keywords>
    <Phrase>Revolutionary wars are inevitable in class society</Phrase>
    <Phrase>War is the continuation of politics</Phrase>
    <Age>24</Age>
    <Pages/>
    <Genre>POLITICAL</Genre>
</Book>
"""
    dct = deserialize(
        text,
        Annotated[Book, XMLEntity("Book")],
        CONFIG
    )
    assert dct == {
        'author': 'Chairman Mao',
        'book_id': 42,
        'title': 'Little Red Book',
        'publication_date': datetime(1973, 1, 1, 21, 52, 13, tzinfo=UTC),
        'keywords': ['Revolution', 'Communism'],
        'phrases': [
            'Revolutionary wars are inevitable in class society',
            'War is the continuation of politics'
        ],
        'age': 24,
        'pages': None,
        'genre': Genre.POLITICAL
    }


def test_xml_deserialize_annotated_with_encoding() -> None:
    """Test for from_xml_element"""

    text = """<?xml version="1.0" encoding="UTF-8"?>
<Book  bookId="42">
    <Title>Little Red Book</Title>
    <Author>Chairman Mao</Author>
    <PublicationDate>1973-01-01T21:52:13Z</PublicationDate>
    <Keywords>
      <Keyword>Revolution</Keyword>
      <Keyword>Communism</Keyword>
    </Keywords>
    <Phrase>Revolutionary wars are inevitable in class society</Phrase>
    <Phrase>War is the continuation of politics</Phrase>
    <Age>24</Age>
    <Pages/>
    <Genre>POLITICAL</Genre>
</Book>
"""
    dct = deserialize(
        text.encode('utf-8'),
        Annotated[Book, XMLEntity("Book")],
        CONFIG
    )
    assert dct == {
        'author': 'Chairman Mao',
        'book_id': 42,
        'title': 'Little Red Book',
        'publication_date': datetime(1973, 1, 1, 21, 52, 13, tzinfo=UTC),
        'keywords': ['Revolution', 'Communism'],
        'phrases': [
            'Revolutionary wars are inevitable in class society',
            'War is the continuation of politics'
        ],
        'age': 24,
        'pages': None,
        'genre': Genre.POLITICAL
    }
