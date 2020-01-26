"""Serialization"""

from datetime import datetime
import re
from typing import (
    Callable,
    Optional,
    Pattern,
    Tuple
)

DATETIME_ZULU_REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$')

DateTimeFormat = Tuple[str, Pattern, Optional[Callable[[str], str]]]

DATETIME_FORMATS: Tuple[DateTimeFormat, ...] = (
    (
        "%Y-%m-%dT%H:%M:%SZ",
        re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'),
        None
    ),
    (
        "%Y-%m-%dT%H:%M:%S.%fZ",
        re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z$'),
        None
    ),
    (
        "%Y-%m-%dT%H:%M:%S%z",
        re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}$'),
        lambda s: s[0:-3] + s[-2:]
    ),
    (
        "%Y-%m-%dT%H:%M:%S.%f%z",
        re.compile(
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+[+-]\d{2}:\d{2}$'),
        lambda s: s[0:-3] + s[-2:]
    )
)


def iso_8601_to_datetime(value: str) -> Optional[datetime]:
    """Parse an ISO 8601 datetime

    Args:
        value (str): The ISO 8601 date string

    Returns:
        Optional[datetime]: A timestamp
    """
    for fmt, pattern, transform in DATETIME_FORMATS:
        if pattern.match(value):
            text = transform(value) if transform else value
            return datetime.strptime(text, fmt)
    raise ValueError(f'Unable to convert "{value}" to a datetime')


def datetime_to_iso_8601(timestamp: datetime) -> str:
    """Convert datetime to ISO 8601

    Args:
        timestamp (datetime): The timestamp

    Returns:
        str: The stringified ISO 8601 version of the timestamp
    """
    date_part = "{year:04d}-{month:02d}-{day:02d}".format(
        year=timestamp.year, month=timestamp.month, day=timestamp.day,
    )
    time_part = "{hour:02d}:{minute:02d}:{second:02d}.{millis:02d}".format(
        hour=timestamp.hour, minute=timestamp.minute, second=timestamp.second,
        millis=timestamp.microsecond // 1000
    )

    utcoffset = timestamp.utcoffset()
    if utcoffset is None:
        return f"{date_part}T{time_part}Z"
    else:
        tz_seconds = utcoffset.total_seconds()
        tz_sign = '-' if tz_seconds < 0 else '+'
        tz_minutes = int(abs(tz_seconds)) // 60
        tz_hours = tz_minutes // 60
        tz_minutes %= 60
        return f"{date_part}T{time_part}{tz_sign}{tz_hours:02d}:{tz_minutes:02d}"
