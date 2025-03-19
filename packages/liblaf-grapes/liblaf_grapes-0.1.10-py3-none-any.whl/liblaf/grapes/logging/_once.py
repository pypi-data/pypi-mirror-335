import functools
from typing import Any

from loguru import logger

# https://stackoverflow.com/a/66062313


@functools.lru_cache
def trace_once(message: Any, *args, **kwargs) -> None:
    logger.trace(message, *args, **kwargs)


@functools.lru_cache
def debug_once(message: Any, *args, **kwargs) -> None:
    logger.debug(message, *args, **kwargs)


@functools.lru_cache
def info_once(message: Any, *args, **kwargs) -> None:
    logger.info(message, *args, **kwargs)


@functools.lru_cache
def success_once(message: Any, *args, **kwargs) -> None:
    logger.success(message, *args, **kwargs)


@functools.lru_cache
def warning_once(message: Any, *args, **kwargs) -> None:
    logger.warning(message, *args, **kwargs)


@functools.lru_cache
def error_once(message: Any, *args, **kwargs) -> None:
    logger.error(message, *args, **kwargs)


@functools.lru_cache
def critical_once(message: Any, *args, **kwargs) -> None:
    logger.critical(message, *args, **kwargs)


@functools.lru_cache
def log_once(level: int | str, message: Any, *args, **kwargs) -> None:
    logger.log(level, message, *args, **kwargs)


@functools.lru_cache
def exception_once(message: Any, *args, **kwargs) -> None:
    logger.exception(message, *args, **kwargs)
