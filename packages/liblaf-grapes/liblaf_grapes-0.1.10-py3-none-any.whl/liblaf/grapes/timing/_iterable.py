from collections.abc import Iterable, Iterator

from . import TimerAttrs, TimerTrait


class TimedIterable[T](TimerTrait):
    iterable: Iterable[T]
    __timer_attrs: TimerAttrs

    @property
    def _timer_attrs(self) -> TimerAttrs:
        return self.__timer_attrs

    def __init__(self, iterable: Iterable[T], timer: TimerTrait) -> None:
        self.__timer_attrs = timer._timer_attrs  # noqa: SLF001
        self.iterable = iterable
        self.label = self.label or "Iterable"

    def __contains__(self, x: object, /) -> bool:
        return x in self.iterable  # pyright: ignore[reportOperatorIssue]

    def __iter__(self) -> Iterator[T]:
        for item in self.iterable:
            self.start()
            yield item
            self.end(depth=3)
        self.log_summary(depth=2)

    def __len__(self) -> int:
        return len(self.iterable)  # pyright: ignore[reportArgumentType]
