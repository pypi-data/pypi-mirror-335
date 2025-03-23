from collections.abc import Callable, Iterable

from . import TimedFunction, TimedIterable, TimerAttrs, TimerTrait, register_timer


class timer(TimerTrait):  # noqa: N801
    __timer_attrs: TimerAttrs

    @property
    def _timer_attrs(self) -> TimerAttrs:
        return self.__timer_attrs

    def __init__(
        self,
        label: str | None = None,
        *,
        counters: Iterable[str] = ["perf", "process"],
        log_summary_at_exit: bool = False,
        record_log_level: int | str | None = "DEBUG",
        summary_log_level: int | str | None = "INFO",
    ) -> None:
        self.__timer_attrs = TimerAttrs(
            label=label,
            log_summary_at_exit=log_summary_at_exit,
            record_log_level=record_log_level,
            summary_log_level=summary_log_level,
        )
        for counter in counters:
            self._records[counter] = []
        if self.log_summary_at_exit:
            register_timer(self)

    def __call__[**P, T](self, fn: Callable[P, T]) -> TimedFunction[P, T]:
        return TimedFunction(fn, self)

    def track[T](self, iterable: Iterable[T]) -> TimedIterable[T]:
        return TimedIterable(iterable, self)
