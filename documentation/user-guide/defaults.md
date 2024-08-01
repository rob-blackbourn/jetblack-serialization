# Defaults

There is a `DefaultValue` annotation. This can
be used in conjunction with the other annotations.

For example:

```python
from datetime import datetime
from typing import List, Optional, TypedDict, Union, Annotated
from jetblack_serialization import DefaultValue

class Book(TypedDict, total=False):
    book_id: int
    title: str
    author: str
    publication_date: datetime
    keywords: List[str]
    phrases: List[str]
    age: Optional[Union[datetime, int]]
    pages: Annnotated[Optional[int], DefaultValue(1)]
```
