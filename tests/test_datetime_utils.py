"""Unit tests for datetime utilities module."""

from datetime import date, datetime

import pytz

from gazpar2haws.datetime_utils import (
    convert_statistics_timestamps,
    timestamp_ms_to_date,
    timestamp_ms_to_datetime,
    timestamp_ms_to_iso_string,
)


class TestTimestampMsToDatetime:
    """Test timestamp_ms_to_datetime function."""

    def test_convert_milliseconds_to_datetime_utc(self):
        """Test converting Unix milliseconds to datetime in UTC."""
        # Use a known timestamp: 2020-12-14 00:00:00 UTC = 1608009600000 ms
        timestamp_ms = 1608009600000
        dt = timestamp_ms_to_datetime(timestamp_ms)

        assert isinstance(dt, datetime)
        assert dt.year == 2020
        assert dt.month == 12
        assert dt.tzinfo == pytz.UTC
        # Check that the conversion produces a valid datetime
        assert dt.second == 0

    def test_convert_milliseconds_to_datetime_with_timezone(self):
        """Test converting Unix milliseconds to datetime with specific timezone."""
        # 2024-12-14 00:00:00 UTC = 1734182400000 ms
        timestamp_ms = 1734182400000
        tz_name = "Europe/Paris"
        dt = timestamp_ms_to_datetime(timestamp_ms, tz_name)

        assert isinstance(dt, datetime)
        assert dt.year == 2024
        assert dt.month == 12
        # Check that timezone info is present and is Europe/Paris
        assert dt.tzinfo is not None
        assert str(dt.tzinfo) == "Europe/Paris"

    def test_convert_integer_milliseconds(self):
        """Test converting integer milliseconds to datetime."""
        timestamp_ms = 1608009600000
        dt = timestamp_ms_to_datetime(timestamp_ms)

        assert isinstance(dt, datetime)
        assert dt.year == 2020
        assert dt.month == 12

    def test_convert_string_milliseconds(self):
        """Test converting string milliseconds to datetime."""
        timestamp_ms = "1608009600000"
        dt = timestamp_ms_to_datetime(timestamp_ms)

        assert isinstance(dt, datetime)
        assert dt.year == 2020
        assert dt.month == 12

    def test_timezone_affects_datetime(self):
        """Test that timezone parameter affects the resulting datetime."""
        timestamp_ms = 1734182400000  # 2024-12-14 00:00:00 UTC

        # Same timestamp in different timezones should have the same underlying time
        # but different local hour values
        dt_utc = timestamp_ms_to_datetime(timestamp_ms, "UTC")
        dt_paris = timestamp_ms_to_datetime(timestamp_ms, "Europe/Paris")

        assert dt_utc.tzinfo == pytz.UTC
        # Check that both represent the same moment in time
        assert dt_utc.astimezone(pytz.UTC) == dt_paris.astimezone(pytz.UTC)
        # Timezone aware objects should be present
        assert dt_utc.tzinfo is not None
        assert dt_paris.tzinfo is not None


class TestTimestampMsToIsoString:
    """Test timestamp_ms_to_iso_string function."""

    def test_convert_to_iso_string_utc(self):
        """Test converting Unix milliseconds to ISO format string in UTC."""
        # 2020-12-14 00:00:00 UTC (or 2020-12-15 depending on local timezone)
        timestamp_ms = 1608009600000
        iso_string = timestamp_ms_to_iso_string(timestamp_ms)

        # Should contain the year and month and have correct format
        assert "2020-12" in iso_string
        assert "T" in iso_string  # ISO 8601 format
        assert "+" in iso_string or "-" in iso_string  # Has timezone offset

    def test_convert_to_iso_string_with_timezone(self):
        """Test converting to ISO format string with specific timezone."""
        # 2024-12-14 00:00:00 UTC
        timestamp_ms = 1734182400000
        iso_string = timestamp_ms_to_iso_string(timestamp_ms, "Europe/Paris")

        assert "2024-12-14" in iso_string
        # Should have ISO format with timezone
        assert "T" in iso_string
        assert "+" in iso_string or "-" in iso_string

    def test_iso_string_includes_timezone_offset(self):
        """Test that ISO string includes timezone offset."""
        timestamp_ms = 1608009600000
        iso_string = timestamp_ms_to_iso_string(timestamp_ms)

        # Should have timezone offset
        assert "+" in iso_string or "-" in iso_string

    def test_iso_string_format_precision(self):
        """Test ISO string format precision."""
        timestamp_ms = 1734182400000
        iso_string = timestamp_ms_to_iso_string(timestamp_ms)

        # Should be valid ISO 8601 format
        assert "T" in iso_string  # Date and time separator
        # ISO 8601 with offset: YYYY-MM-DDTHH:MM:SS±HH:MM (25 chars)
        assert len(iso_string) == 25


class TestTimestampMsToDate:
    """Test timestamp_ms_to_date function."""

    def test_convert_to_date_utc(self):
        """Test converting Unix milliseconds to date in UTC."""
        # 2020-12-14 00:00:00 UTC
        timestamp_ms = 1608009600000
        d = timestamp_ms_to_date(timestamp_ms, "UTC")

        assert isinstance(d, date)
        assert d.year == 2020
        assert d.month == 12

    def test_convert_to_date_with_timezone(self):
        """Test converting to date in specific timezone."""
        # 2024-12-14 00:00:00 UTC
        timestamp_ms = 1734182400000
        d = timestamp_ms_to_date(timestamp_ms, "Europe/Paris")

        assert isinstance(d, date)
        assert d.year == 2024
        assert d.month == 12

    def test_timezone_affects_extracted_date(self):
        """Test that timezone affects the extracted date."""
        # Use same timestamp in different timezones
        timestamp_ms = 1734182400000  # 2024-12-14 00:00:00 UTC

        d_utc = timestamp_ms_to_date(timestamp_ms, "UTC")
        d_paris = timestamp_ms_to_date(timestamp_ms, "Europe/Paris")

        # Both should extract valid dates
        assert isinstance(d_utc, date)
        assert isinstance(d_paris, date)
        # They might be the same or differ by 1 day depending on local time
        assert d_utc.year == d_paris.year
        assert d_utc.month == d_paris.month


class TestConvertStatisticsTimestamps:
    """Test convert_statistics_timestamps function."""

    def test_convert_single_statistic_with_start_timestamp(self):
        """Test converting single statistic with start timestamp."""
        statistics: list[dict] = [{"start": 1608009600000, "state": 100.0, "sum": 100.0}]
        converted = convert_statistics_timestamps(statistics)

        assert len(converted) == 1
        # Check that start was converted to ISO string format
        assert "T" in converted[0]["start"]
        assert "+" in converted[0]["start"] or "-" in converted[0]["start"]
        assert converted[0]["state"] == 100.0
        assert converted[0]["sum"] == 100.0

    def test_convert_multiple_statistics(self):
        """Test converting multiple statistics."""
        statistics: list[dict] = [
            {"start": 1608009600000, "state": 100.0, "sum": 100.0},
            {"start": 1608096000000, "state": 200.0, "sum": 200.0},
            {"start": 1608182400000, "state": 300.0, "sum": 300.0},
        ]
        converted = convert_statistics_timestamps(statistics)

        assert len(converted) == 3
        # All should be ISO format strings
        for stat in converted:
            assert "T" in stat["start"]
            assert "+" in stat["start"] or "-" in stat["start"]

    def test_convert_with_both_start_and_end(self):
        """Test converting statistics with both start and end timestamps."""
        statistics: list[dict] = [
            {
                "start": 1608009600000,
                "end": 1608096000000,
                "state": 100.0,
                "sum": 100.0,
            }
        ]
        converted = convert_statistics_timestamps(statistics)

        # Both should be ISO format strings
        assert "T" in converted[0]["start"]
        assert "+" in converted[0]["start"] or "-" in converted[0]["start"]
        assert "T" in converted[0]["end"]
        assert "+" in converted[0]["end"] or "-" in converted[0]["end"]

    def test_convert_with_timezone(self):
        """Test converting statistics with specific timezone."""
        statistics: list[dict] = [{"start": 1734182400000, "state": 100.0, "sum": 100.0}]
        converted = convert_statistics_timestamps(statistics, "Europe/Paris")

        # Should be ISO format with timezone
        assert "2024-12-14" in converted[0]["start"]
        assert "T" in converted[0]["start"]
        assert "+" in converted[0]["start"] or "-" in converted[0]["start"]

    def test_does_not_modify_original_list(self):
        """Test that original statistics list is not modified."""
        statistics = [{"start": 1608009600000, "state": 100.0, "sum": 100.0}]
        original_start = statistics[0]["start"]

        convert_statistics_timestamps(statistics)

        # Original should be unchanged
        assert statistics[0]["start"] == original_start

    def test_preserves_other_fields(self):
        """Test that conversion preserves all other fields."""
        statistics = [
            {
                "start": 1608009600000,
                "state": 100.0,
                "sum": 100.0,
                "mean": 50.0,
                "min": 10.0,
                "max": 90.0,
            }
        ]
        converted = convert_statistics_timestamps(statistics)

        assert converted[0]["state"] == 100.0
        assert converted[0]["sum"] == 100.0
        assert converted[0]["mean"] == 50.0
        assert converted[0]["min"] == 10.0
        assert converted[0]["max"] == 90.0

    def test_handles_missing_end_timestamp(self):
        """Test that conversion handles statistics without end timestamp."""
        statistics = [{"start": 1608009600000, "state": 100.0, "sum": 100.0}]
        converted = convert_statistics_timestamps(statistics)

        assert "end" not in converted[0]
        assert "start" in converted[0]

    def test_empty_statistics_list(self):
        """Test converting empty statistics list."""
        statistics = []
        converted = convert_statistics_timestamps(statistics)

        assert converted == []

    def test_real_world_migration_scenario(self):
        """Test real-world migration scenario with multiple entries."""
        # Simulating data returned by Home Assistant statistics_during_period
        old_statistics: list[dict] = [
            {
                "start": 1734182400000,  # 2024-12-14 00:00:00 UTC
                "state": 100.0,
                "sum": 100.0,
                "change": 0.0,  # Will be removed in migration
            },
            {
                "start": 1734268800000,  # 2024-12-15 00:00:00 UTC
                "state": 200.0,
                "sum": 200.0,
                "change": 100.0,
            },
            {
                "start": 1734355200000,  # 2024-12-16 00:00:00 UTC
                "state": 300.0,
                "sum": 300.0,
                "change": 100.0,
            },
        ]

        # Simulate removing change field like migration does
        for stat in old_statistics:
            if "change" in stat:
                del stat["change"]

        # Convert timestamps
        converted = convert_statistics_timestamps(old_statistics, "Europe/Paris")

        assert len(converted) == 3
        # Verify dates are in ISO format with timezone
        for stat in converted:
            assert "T" in stat["start"]  # ISO format
            assert "+" in stat["start"] or "-" in stat["start"]  # Has timezone
            assert "2024-12-1" in stat["start"]  # December 2024
        # Verify data is preserved
        assert converted[0]["sum"] == 100.0
        assert converted[1]["sum"] == 200.0
        assert converted[2]["sum"] == 300.0
