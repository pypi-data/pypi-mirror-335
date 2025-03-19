import os
from pathlib import Path
from typing import Unpack

import loguru
from environs import env
from rich.console import Console

from liblaf import grapes

from . import Filter, default_filter


def console_handler(
    console: Console | None = None,
    filter_: Filter | None = None,
    **kwargs: Unpack["loguru.BasicHandlerConfig"],
) -> "loguru.HandlerConfig":
    if console is None:
        console = grapes.logging_console()
    if filter_ is None:
        filter_ = default_filter()

    def sink(message: "loguru.Message") -> None:
        console.print(message, end="", no_wrap=True, crop=False, overflow="ignore")

    return {
        "sink": sink,
        "format": "[green]{time:YYYY-MM-DD HH:mm:ss.SSS}[/green] | [logging.level.{level}]{level: <8}[/logging.level.{level}] | [cyan]{name}[/cyan]:[cyan]{function}[/cyan]:[cyan]{line}[/cyan] - {message}",
        "filter": filter_,
        **kwargs,
    }


def file_handler(
    fpath: str | os.PathLike[str] | None = None,
    filter_: Filter | None = None,
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.HandlerConfig":
    if fpath is None:
        fpath = env.path("LOGGING_FILE", default=Path("run.log"))
    if filter_ is None:
        filter_ = default_filter()
    return {"sink": fpath, "filter": filter_, "mode": "w", **kwargs}


def jsonl_handler(
    fpath: str | os.PathLike[str] | None = None,
    filter_: Filter | None = None,
    **kwargs: Unpack["loguru.FileHandlerConfig"],
) -> "loguru.HandlerConfig":
    if fpath is None:
        fpath = env.path("LOGGING_JSONL", default=Path("run.log.jsonl"))
    if filter_ is None:
        filter_ = default_filter()
    return {"sink": fpath, "filter": filter_, "serialize": True, "mode": "w", **kwargs}
