import logging
from collections.abc import Sequence

import loguru
from environs import Env
from loguru import logger

from liblaf import grapes

from . import (
    DEFAULT_LEVELS,
    Filter,
    add_level,
    console_handler,
    file_handler,
    jsonl_handler,
    setup_loguru_logging_intercept,
)


def init_loguru(
    level: int | str = logging.NOTSET,
    filter_: Filter | None = None,
    handlers: Sequence["loguru.HandlerConfig"] | None = None,
    levels: Sequence["loguru.LevelConfig"] | None = None,
) -> None:
    """Initialize the Loguru logger with specified configurations.

    Args:
        level: The logging level.
        filter_: A filter to apply to the logger.
        handlers: A sequence of handler configurations.
        levels: A sequence of level configurations.
    """
    if handlers is None:
        handlers: list[loguru.HandlerConfig] = [
            console_handler(level=level, filter_=filter_)
        ]
        env: Env = grapes.environ.init_env()
        if fpath := env.path("LOGGING_FILE", None):
            handlers.append(file_handler(fpath, level=level, filter_=filter_))
        if fpath := env.path("LOGGING_JSONL", None):
            handlers.append(jsonl_handler(fpath, level=level, filter_=filter_))
    logger.configure(handlers=handlers)
    for lvl in levels or DEFAULT_LEVELS:
        add_level(**lvl)
    setup_loguru_logging_intercept(level=level)
