import loguru

from . import Filter, as_filter_func


def filter_all(*filters: Filter) -> "loguru.FilterFunction":
    filters: list[loguru.FilterFunction] = [
        fn for f in filters if (fn := as_filter_func(f)) is not None
    ]

    def filter_(record: "loguru.Record") -> bool:
        return all(fn(record) for fn in filters)

    return filter_


def filter_any(*filters: Filter) -> "loguru.FilterFunction":
    filters: list[loguru.FilterFunction] = [
        fn for f in filters if (fn := as_filter_func(f)) is not None
    ]

    def filter_(record: "loguru.Record") -> bool:
        return any(fn(record) for fn in filters)

    return filter_
