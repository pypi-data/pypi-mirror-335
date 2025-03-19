import abc
import contextlib
import types
from typing import Self

import attrs

from . import TimerRecordsAttrs, TimerRecordsTrait, get_time


@attrs.define
class TimerAttrs(TimerRecordsAttrs):
    end: dict[str, float] = attrs.field(factory=dict)
    start: dict[str, float] = attrs.field(factory=dict)


class TimerTrait(contextlib.AbstractContextManager, TimerRecordsTrait):
    # region attrs

    @property
    @abc.abstractmethod
    def _timer_attrs(self) -> TimerAttrs: ...

    @property
    def _end(self) -> dict[str, float]:
        return self._timer_attrs.end

    @property
    def _start(self) -> dict[str, float]:
        return self._timer_attrs.start

    @property
    def _timer_records_attrs(self) -> TimerRecordsAttrs:
        return self._timer_attrs

    # endregion attrs

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.end(depth=3)

    def start(self) -> None:
        for counter in self.columns:
            self._start[counter] = get_time(counter)

    def end(self, depth: int = 2) -> None:
        for counter in self.columns:
            self._end[counter] = get_time(counter)
        self.append(
            {
                counter: self._end[counter] - self._start[counter]
                for counter in self.columns
            }
        )
        self.log_record(depth=depth)
