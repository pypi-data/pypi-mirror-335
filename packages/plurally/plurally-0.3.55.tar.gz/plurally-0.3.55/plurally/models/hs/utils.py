from datetime import datetime, timezone

from loguru import logger


def validate_timestamp(v):
    if isinstance(v, datetime):
        return int(v.timestamp())
    if isinstance(v, (int, float)):
        return int(v)
    if isinstance(v, str):
        try:
            return int(datetime.fromisoformat(v).timestamp())
        except Exception:
            logger.error(f"Unexpected timestamp: {v}")
    return int(datetime.now(tz=timezone.utc).timestamp())
