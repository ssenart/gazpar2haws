"""Utility functions for datetime conversions."""

from datetime import date, datetime

import pytz


def timestamp_ms_to_datetime(timestamp_ms: int | float | str, timezone: str | None = None) -> datetime:
    """
    Convert Unix timestamp in milliseconds to a datetime object.

    This is the base conversion function used by other timestamp utilities.

    Args:
        timestamp_ms: Unix timestamp in milliseconds (as int, float, or string)
        timezone: Optional timezone string for timezone-aware datetime.
                 If provided, creates datetime in that timezone.
                 If not provided, uses UTC (default Home Assistant behavior).

    Returns:
        datetime object in the specified timezone or UTC
    """
    # Convert to seconds
    timestamp_seconds = int(str(timestamp_ms)) / 1000
    # Convert to specified timezone or UTC
    if timezone:
        return datetime.fromtimestamp(timestamp_seconds, tz=pytz.timezone(timezone))
    return datetime.fromtimestamp(timestamp_seconds, tz=pytz.UTC)


def timestamp_ms_to_iso_string(timestamp_ms: int | float | str, timezone: str | None = None) -> str:
    """
    Convert Unix timestamp in milliseconds to ISO format string.

    This is used for converting Home Assistant statistics timestamps
    (which are in milliseconds) to ISO format strings expected by
    the import_statistics API.

    Args:
        timestamp_ms: Unix timestamp in milliseconds (as int, float, or string)
        timezone: Optional timezone string for timezone-aware conversion.
                 If provided, converts to that timezone before returning ISO format.
                 If not provided, uses UTC (default Home Assistant behavior).

    Returns:
        ISO format string (e.g., "2020-12-14T00:00:00+00:00")
    """
    dt = timestamp_ms_to_datetime(timestamp_ms, timezone)
    return dt.isoformat()


def timestamp_ms_to_date(timestamp_ms: int | float | str, timezone: str) -> date:
    """
    Convert Unix timestamp in milliseconds to a date in the specified timezone.

    This is used for extracting the date portion of Home Assistant statistics
    timestamps while respecting the local timezone.

    Args:
        timestamp_ms: Unix timestamp in milliseconds (as int, float, or string)
        timezone: Timezone string (e.g., "Europe/Paris")

    Returns:
        Date object in the specified timezone
    """
    dt = timestamp_ms_to_datetime(timestamp_ms, timezone)
    return dt.date()


def convert_statistics_timestamps(statistics: list[dict], timezone: str | None = None) -> list[dict]:
    """
    Convert all timestamp fields in statistics from Unix milliseconds to ISO format strings.

    Home Assistant statistics_during_period API returns timestamps as Unix milliseconds,
    but the import_statistics API expects ISO format strings.

    Converts these fields if they exist:
    - "start": The start time of the statistics period
    - "end": The end time of the statistics period (if present)

    Args:
        statistics: List of statistics dictionaries with timestamp fields
        timezone: Optional timezone string for timezone-aware conversion.
                 If provided, converts to that timezone before returning ISO format.
                 If not provided, uses UTC (default Home Assistant behavior).

    Returns:
        List of statistics dictionaries with converted timestamps
    """
    converted_statistics = []
    for stat in statistics:
        converted_stat = stat.copy()

        # Convert start timestamp if present
        if "start" in converted_stat:
            converted_stat["start"] = timestamp_ms_to_iso_string(converted_stat["start"], timezone)

        # Convert end timestamp if present (for statistics that have it)
        if "end" in converted_stat:
            converted_stat["end"] = timestamp_ms_to_iso_string(converted_stat["end"], timezone)

        converted_statistics.append(converted_stat)

    return converted_statistics
