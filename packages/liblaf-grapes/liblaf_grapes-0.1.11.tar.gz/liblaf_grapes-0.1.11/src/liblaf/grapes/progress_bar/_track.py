from collections.abc import Generator, Iterable

from rich.progress import Progress

from liblaf import grapes

from . import progress


def track[T](
    sequence: Iterable[T],
    *,
    description: str | bool | None = True,
    record_log_level: int | str | None = "DEBUG",
    summary_log_level: int | str | None = "INFO",
    timer: bool = True,
    total: float | None = None,
) -> Generator[T]:
    """Tracks the progress of iterating over a sequence with optional logging and timing.

    Args:
        sequence: The sequence to iterate over.
        description: Description for the progress bar. If `True`, uses caller location.
        record_log_level: Log level for recording progress.
        summary_log_level: Log level for reporting progress.
        timer: Whether to use a timer for tracking.
        total: Total number of items in the sequence.

    Yields:
        Yields items from the sequence.
    """
    if description is True:
        description = grapes.caller_location(2)
    description = description or ""
    prog: Progress = progress()
    if timer:
        t = grapes.timer(
            label=description,
            log_summary_at_exit=False,
            record_log_level=record_log_level,
            summary_log_level=summary_log_level,
        )
        with prog:
            yield from t.track(
                prog.track(sequence, total=total, description=description)
            )
            t.log_summary()
    else:
        with prog:
            yield from prog.track(sequence, description=description)
