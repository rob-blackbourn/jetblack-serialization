"""Tests for JSON serialization"""

from datetime import timezone, timedelta

from jetblack_serialization.iso_8601 import (
    iso_8601_to_datetime,
    datetime_to_iso_8601
)


def test_roundtrip():
    """Test for iso 8601"""
    for text in [
            '2014-01-01T23:28:56.782Z',
            '2014-02-01T09:28:56.321-10:00',
            '2014-02-01T09:28:56.321+00:00'
    ]:
        timestamp = iso_8601_to_datetime(text)
        roundtrip = datetime_to_iso_8601(timestamp)
        assert text == roundtrip


def test_zulu_tz_winter():
    """Test for the zulu timezone"""
    timestamp = iso_8601_to_datetime('2014-01-01T23:28:56.782Z')
    assert timestamp.timetuple() == (2014, 1, 1, 23, 28, 56, 2, 1, -1)
    assert timestamp.tzinfo is None


def test_zulu_tz_summer():
    """Test for the zulu timezone"""
    timestamp = iso_8601_to_datetime('2014-08-01T23:28:56.782Z')
    assert timestamp.timetuple() == (2014, 8, 1, 23, 28, 56, 4, 213, -1)
    assert timestamp.tzinfo is None


def test_tz_offset():
    """Test for timezone offset"""
    timestamp = iso_8601_to_datetime('2014-02-01T09:28:56.321-10:00')
    assert timestamp.timetuple() == (2014, 2, 1, 9, 28, 56, 5, 32, -1)
    assert timestamp.tzinfo == timezone(timedelta(hours=-10))


def test_tz_offset_0():
    """Test for timezone offset"""
    timestamp = iso_8601_to_datetime('2014-02-01T09:28:56.321+00:00')
    assert timestamp.timetuple() == (2014, 2, 1, 9, 28, 56, 5, 32, -1)
    assert timestamp.tzinfo == timezone(timedelta(hours=0))
