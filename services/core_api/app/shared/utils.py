"""Shared utility functions."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get current UTC time.

    Returns:
        datetime: Current UTC datetime.
    """
    return datetime.now(timezone.utc)
