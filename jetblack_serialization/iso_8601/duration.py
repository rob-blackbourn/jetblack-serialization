"""ISO 8601 duration"""

from datetime import timedelta
import re
from typing import Optional

# pylint: disable=line-too-long
DURATION_REGEX = re.compile(
    r'^(-?)P(?=\d|T\d)(?:(\d+)Y)?(?:(\d+)M)?(?:(\d+)([DW]))?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?$'
)

DAYS_IN_MONTH = 30
DAYS_IN_YEAR = DAYS_IN_MONTH * 12
SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 60 * 60
SECONDS_IN_DAY = 24 * SECONDS_IN_HOUR


def _parse_int(value: Optional[str]) -> int:
    return 0 if not value else int(value)


def _parse_sign(value: Optional[str]) -> int:
    return -1 if value == '-' else 1


def iso_8601_to_timedelta(duration: str) -> Optional[timedelta]:
    """Convert an ISO 8601 duration to a timedelta

    Args:
        duration (str): An ISO 8601 format duration

    Returns:
        Optional[timedelta]: The duration as a timedelta
    """
    match = DURATION_REGEX.match(duration)
    if not match:
        raise ValueError(f'Unable to convert "{duration}" to a timedelta.')
    sign = _parse_sign(match.group(1))
    years = _parse_int(match.group(2))
    months = _parse_int(match.group(3))
    days_or_weeks = _parse_int(match.group(4))
    is_weeks = match.group(5) == 'W'
    hours = _parse_int(match.group(6))
    minutes = _parse_int(match.group(7))
    seconds = _parse_int(match.group(8))

    total_days = days_or_weeks * 7 if is_weeks else days_or_weeks
    total_days += months * DAYS_IN_MONTH
    total_days += years * DAYS_IN_YEAR

    total_seconds = seconds
    total_seconds += minutes * SECONDS_IN_MINUTE
    total_seconds += hours * SECONDS_IN_HOUR
    total_seconds += total_days * SECONDS_IN_DAY

    total_seconds *= sign

    return timedelta(seconds=total_seconds)


def timedelta_to_iso_8601(value: timedelta) -> str:
    """Convert a timedelta to an ISO 8601 duration string

    Prefers weeks to days, so a roundtrip of P7D becomes P1W. Also an zero value
    is removed. A zero duration becomes P0D.

    Args:
        value (timedelta): A timedelta

    Returns:
        str: The ISO 8601 duration representation of the timedelta.
    """
    total_seconds = int(value.total_seconds())

    sign = -1 if total_seconds < 0 else 1
    total_seconds *= sign

    total_days = total_seconds // SECONDS_IN_DAY
    total_seconds %= SECONDS_IN_DAY

    years = total_days // DAYS_IN_YEAR
    total_days %= DAYS_IN_YEAR
    months = total_days // DAYS_IN_MONTH
    total_days %= DAYS_IN_MONTH
    days = total_days
    is_weeks = days % 7 == 0
    if is_weeks:
        weeks = days // 7
        days = 0
    else:
        weeks = 0

    hours = total_seconds // SECONDS_IN_HOUR
    total_seconds %= SECONDS_IN_HOUR
    minutes = total_seconds // SECONDS_IN_MINUTE
    total_seconds %= SECONDS_IN_MINUTE
    seconds = total_seconds

    duration = ''

    if years:
        duration += str(years) + 'Y'
    if months:
        duration += str(months) + 'M'
    if is_weeks:
        if weeks:
            duration += str(weeks) + 'W'
    else:
        if days:
            duration += str(days) + 'D'

    if hours or minutes or seconds:
        duration += 'T'
        if hours:
            duration += str(hours) + 'H'
        if minutes:
            duration += str(minutes) + 'M'
        if seconds:
            duration += str(seconds) + 'S'

    if not duration:
        duration = '0D'

    return 'P' + duration if sign == 1 else '-P' + duration
