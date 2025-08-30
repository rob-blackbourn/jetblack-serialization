from typing import Callable

from lxml import etree
from lxml.etree import _Element  # pylint: disable=no-name-in-module

type XMLEncoder = Callable[[_Element], str]
type XMLDecoder = Callable[[str | bytes | bytearray], _Element]


def ENCODE_XML(element: _Element) -> str:
    return etree.tostring(element).decode()


def DECODE_XML(text: str | bytes | bytearray) -> _Element:
    return etree.fromstring(text)
