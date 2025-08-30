# Defaults

There is a `DefaultValue` annotation. This can
be used in conjunction with the other annotations.

For example:

```python
from datetime import datetime
from typing import Optional, TypedDict, Union, Annotated
from jetblack_serialization import DefaultValue

class Book(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: list[str]
    phrases: list[str]
    age: Optional[Union[datetime, int]]
    pages: Annotated[Optional[int], DefaultValue(1)]
```
