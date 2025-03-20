from datetime import UTC, datetime
from typing import Any, NoReturn


def utc_now() -> datetime:
    return datetime.now(UTC)


def raise_(msg: str) -> NoReturn:
    raise RuntimeError(msg)


MM_JINJA_GLOBALS: dict[str, Any] = {
    "raise": raise_,
    "utc_now": utc_now,
}
