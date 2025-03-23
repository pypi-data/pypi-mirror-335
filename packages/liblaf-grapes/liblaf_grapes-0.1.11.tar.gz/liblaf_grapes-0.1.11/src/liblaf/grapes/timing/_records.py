import abc
import collections
import functools
import statistics
import textwrap
from collections.abc import Iterator, Mapping, Sequence
from typing import overload

import attrs
from loguru import logger

from liblaf import grapes


@attrs.define
class TimerRecordsAttrs:
    label: str | None = None
    log_summary_at_exit: bool = False
    record_log_level: int | str | None = "DEBUG"
    records: dict[str, list[float]] = attrs.field(
        factory=lambda: collections.defaultdict(list)
    )
    summary_log_level: int | str | None = "INFO"


class TimerRecordsTrait(abc.ABC):
    # region attrs

    @property
    @abc.abstractmethod
    def _timer_records_attrs(self) -> TimerRecordsAttrs: ...

    @property
    def label(self) -> str | None:
        return self._timer_records_attrs.label

    @label.setter
    def label(self, value: str | None) -> None:
        self._timer_records_attrs.label = value

    @property
    def log_summary_at_exit(self) -> bool:
        return self._timer_records_attrs.log_summary_at_exit

    @property
    def record_log_level(self) -> int | str | None:
        return self._timer_records_attrs.record_log_level

    @property
    def summary_log_level(self) -> int | str | None:
        return self._timer_records_attrs.summary_log_level

    @property
    def _records(self) -> dict[str, list[float]]:
        return self._timer_records_attrs.records

    # endregion attrs

    @overload
    def __getitem__(self, index: int) -> Mapping[str, float]: ...
    @overload
    def __getitem__(self, index: str) -> Sequence[float]: ...
    def __getitem__(self, index: int | str) -> Mapping[str, float] | Sequence[float]:
        if isinstance(index, int):
            return self.row(index)
        return self.column(index)

    def __len__(self) -> int:
        return self.count

    @property
    def columns(self) -> Sequence[str]:
        return list(self._records.keys())

    @property
    def count(self) -> int:
        return self.n_rows

    @functools.cached_property
    def default_key(self) -> str:
        return next(iter(self._records))

    @property
    def n_columns(self) -> int:
        return len(self._records)

    @property
    def n_rows(self) -> int:
        return len(self.column())

    def append(
        self, seconds: Mapping[str, float] = {}, nanoseconds: Mapping[str, float] = {}
    ) -> None:
        for key, value in seconds.items():
            self._records[key].append(value)
        for key, value in nanoseconds.items():
            self._records[key].append(value * 1e-9)

    def column(self, key: str | None = None) -> Sequence[float]:
        return self._records[key or self.default_key]

    def human_record(self, index: int = -1, label: str | None = None) -> str:
        label: str = self.label or "Timer"
        text: str = f"{label} > "
        for key, value in self.row(index).items():
            human_duration: str = grapes.human_duration(value)
            text += f"{key}: {human_duration}, "
        text = text.strip(", ")
        return text

    def human_summary(self, label: str | None = None) -> str:
        label: str = label or self.label or "Timer"
        header: str = f"{label} (total: {self.n_rows})"
        if self.n_rows == 0:
            return header
        body: str = ""
        for k in self.columns:
            body += f"{k} > "
            human_mean: str = grapes.human_duration_series(self.column(k))
            human_best: str = grapes.human_duration(self.min(k))
            body += f"mean: {human_mean}, best: {human_best}\n"
        body = body.strip()
        summary: str = header + "\n" + textwrap.indent(body, "  ")
        return summary

    def iter_columns(self) -> Iterator[tuple[str, Sequence[float]]]:
        yield from self._records.items()

    def iter_rows(self) -> Iterator[Mapping[str, float]]:
        for index in range(self.n_rows):
            yield self.row(index)

    def log_record(
        self,
        index: int = -1,
        label: str | None = None,
        depth: int = 1,
        level: int | str | None = None,
    ) -> None:
        level = level or self.record_log_level
        if level is None:
            return
        logger.opt(depth=depth).log(level, self.human_record(index=index, label=label))

    def log_summary(
        self, label: str | None = None, depth: int = 1, level: int | str | None = None
    ) -> None:
        level = level or self.summary_log_level
        if level is None:
            return
        logger.opt(depth=depth).log(level, self.human_summary(label=label))

    def row(self, index: int = -1) -> Mapping[str, float]:
        return {key: values[index] for key, values in self._records.items()}

    # region statistics

    def max(self, key: str | None = None) -> float:
        return max(self.column(key))

    def mean(self, key: str | None = None) -> float:
        return statistics.mean(self.column(key))

    def min(self, key: str | None = None) -> float:
        return min(self.column(key))

    def std(self, key: str | None = None) -> float:
        return statistics.stdev(self.column(key))

    # endregion statistics
