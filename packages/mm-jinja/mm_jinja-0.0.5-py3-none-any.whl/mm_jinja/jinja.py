from collections.abc import Callable
from typing import Any

from jinja2 import BaseLoader, Environment

from mm_jinja.filters import MM_JINJA_FILTERS
from mm_jinja.globals import MM_JINJA_GLOBALS


def init_jinja(
    loader: BaseLoader,
    custom_globals: dict[str, Any] | None = None,
    custom_filters: dict[str, Callable[..., Any]] | None = None,
    enable_async: bool = False,
) -> Environment:
    env = Environment(loader=loader, autoescape=True, enable_async=enable_async)
    env.filters |= MM_JINJA_FILTERS
    env.globals |= MM_JINJA_GLOBALS

    if custom_filters:
        env.filters |= custom_filters
    if custom_globals:
        env.globals |= custom_globals

    return env
