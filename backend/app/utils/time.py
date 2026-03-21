from datetime import datetime, timedelta, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def period_start(period: str) -> datetime | None:
    period_map = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }
    days = period_map.get(period)
    if days is None:
        return None
    return utcnow() - timedelta(days=days)
