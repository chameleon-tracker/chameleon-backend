import datetime


def to_internal_mapping(value: str) -> datetime.datetime:
    return as_utc(datetime.datetime.fromisoformat(value))


def to_external_value(value: datetime.datetime) -> str:
    """Convert to UTC timezone and format using ISO datetime format."""
    return as_utc(value).isoformat()


def as_utc(value: datetime.datetime) -> datetime.datetime:
    return value.astimezone(datetime.UTC)


def utcnow() -> datetime.datetime:
    """Returns now with UTC timezone."""
    return datetime.datetime.now(datetime.UTC)
