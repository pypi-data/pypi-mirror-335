from datetime import datetime, timezone

import dateparser


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def dt_parse(dt: str | int) -> datetime:
    parsed_dt: datetime | None = dateparser.parse(str(dt))
    if not parsed_dt:
        raise ValueError("Could not parse the token expiry date.")
    return parsed_dt
