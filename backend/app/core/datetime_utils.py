from datetime import datetime, timezone


def as_aware_utc(value: datetime) -> datetime:
    """Make a `DateTime(timezone=True)` value safely comparable to `datetime.now(timezone.utc)`.

    SQLite drops tzinfo on read (values are stored as UTC, so naive results
    represent UTC), while PostgreSQL returns them already timezone-aware in
    the session's offset. Blindly calling `.replace(tzinfo=timezone.utc)` on
    an aware, non-UTC-offset value silently shifts the instant it represents
    — only naive values need that treatment; aware ones compare correctly
    across offsets as-is.
    """
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
