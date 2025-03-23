import functools
from collections.abc import Callable

from liblaf import grapes

from . import TimerAttrs, TimerTrait


class TimedFunction[**P, T](TimerTrait):
    fn: Callable[P, T]
    __timer_attrs: TimerAttrs

    @property
    def _timer_attrs(self) -> TimerAttrs:
        return self.__timer_attrs

    def __init__(self, fn: Callable[P, T], timer: TimerTrait) -> None:
        self.__timer_attrs = timer._timer_attrs  # noqa: SLF001
        self.fn = fn
        self.label = self.label or grapes.full_qual_name(fn) or "Function"
        functools.update_wrapper(self, fn)

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:  # pyright: ignore[reportIncompatibleMethodOverride]
        self.start()
        result: T = self.fn(*args, **kwargs)
        self.end(depth=3)
        return result
