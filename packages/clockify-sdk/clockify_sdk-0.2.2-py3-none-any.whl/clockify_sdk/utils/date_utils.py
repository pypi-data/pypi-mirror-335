"""
Date and time utility functions
"""

from datetime import datetime, timezone


def format_date(date: datetime) -> str:
    """
    Format a datetime object as a string for Clockify API

    Args:
        date: Datetime object to format

    Returns:
        ISO 8601 formatted UTC time string with Z suffix
    """
    return date.isoformat().replace("+00:00", "Z")


def get_current_utc_time() -> str:
    """
    Get current UTC time formatted for Clockify API

    Returns:
        ISO 8601 formatted UTC time string with Z suffix
    """
    return format_date(datetime.now(timezone.utc))


def format_datetime(dt: datetime) -> str:
    """
    Format a datetime object to ISO 8601 format with UTC timezone

    Args:
        dt: Datetime object to format

    Returns:
        ISO 8601 formatted string with UTC timezone
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)  # Set timezone to UTC if naive
    else:
        dt = dt.astimezone(timezone.utc)  # Convert to UTC if already timezone-aware
    return dt.isoformat().replace("+00:00", "Z")
