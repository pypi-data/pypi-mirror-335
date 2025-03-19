import logging
from collections.abc import Sequence

import loguru

from . import init_icecream, init_loguru, init_rich


def init_logging(
    level: int | str = logging.NOTSET,
    *,
    handlers: Sequence["loguru.HandlerConfig"] | None = None,
    levels: Sequence["loguru.LevelConfig"] | None = None,
    traceback_show_locals: bool = True,
) -> None:
    """Initializes the logging configuration for the application.

    This function sets up logging using Rich, Loguru, and IceCream libraries.

    Args:
        level: The logging level.
        handlers: A sequence of Loguru handler configurations.
        levels: A sequence of Loguru level configurations.
        traceback_show_locals: Whether to show local variables in tracebacks.
    """
    init_rich(show_locals=traceback_show_locals)
    init_loguru(level=level, handlers=handlers, levels=levels)
    init_icecream()
