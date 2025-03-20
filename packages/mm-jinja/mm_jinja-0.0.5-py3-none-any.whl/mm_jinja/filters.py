import json
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal

from markupsafe import Markup


def timestamp(value: datetime | int | None, format_: str = "%Y-%m-%d %H:%M:%S") -> str:
    if isinstance(value, datetime):
        return value.strftime(format_)
    if isinstance(value, int):
        return datetime.fromtimestamp(value).strftime(format_)  # noqa: DTZ006
    return ""


def empty(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, Sequence) and len(value) == 0:
        return ""
    return value


def yes_no(
    value: object, is_colored: bool = True, hide_no: bool = False, none_is_false: bool = False, on_off: bool = False
) -> Markup:
    clr = "black"
    if none_is_false and value is None:
        value = False

    if value is True:
        value = "on" if on_off else "yes"
        clr = "green"
    elif value is False:
        value = "" if hide_no else "off" if on_off else "no"
        clr = "red"
    elif value is None:
        value = ""
    if not is_colored:
        clr = "black"
    return Markup(f"<span style='color: {clr};'>{value}</span>")  # nosec  # noqa: S704


def nformat(
    value: str | float | Decimal | None,
    prefix: str = "",
    suffix: str = "",
    separator: str = "",
    hide_zero: bool = False,
    digits: int = 2,
) -> str:
    if value is None or value == "":
        return ""
    if float(value) == 0:
        if hide_zero:
            return ""
        return f"{prefix}0{suffix}"
    if float(value) > 1000:
        value = "".join(
            reversed([x + (separator if i and not i % 3 else "") for i, x in enumerate(reversed(str(int(value))))]),
        )
    else:
        value = round(value, digits)  # type: ignore[assignment, arg-type]

    return f"{prefix}{value}{suffix}"


def json_url_encode(data: dict[str, object]) -> str:
    return json.dumps(data)


MM_JINJA_FILTERS = {
    "timestamp": timestamp,
    "dt": timestamp,
    "empty": empty,
    "yes_no": yes_no,
    "nformat": nformat,
    "n": nformat,
    "json_url_encode": json_url_encode,
}
