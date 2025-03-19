import bisect
import functools
import operator
from collections.abc import Callable
from typing import Any, Literal, NamedTuple, NoReturn

from liblaf.grapes import Decorator


class Function(NamedTuple):
    condition: Callable[..., bool]
    function: Callable
    priority: int


class NotFoundLookupError(LookupError): ...


def _always_true(*args, **kwargs) -> Literal[True]:  # noqa: ARG001
    return True


def _dummy_final(*args, **kwargs) -> NoReturn:  # noqa: ARG001
    msg: str = "No condition matched."
    raise NotFoundLookupError(msg)


class ConditionalDispatcher:
    registry: list[Function]
    _final: Callable

    def __init__(self) -> None:
        self.registry = []
        self._final = _dummy_final

    def __call__(self, *args, **kwargs) -> Any:
        for func in self.registry:
            try:
                if func.condition(*args, **kwargs):
                    return func.function(*args, **kwargs)
            except TypeError:
                continue
        return self._final(*args, **kwargs)

    def final(self, *, fallback: bool = False) -> Decorator:
        def decorator[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
            if fallback:
                self._final = fn
            else:
                self._final = _dummy_final
            functools.update_wrapper(self, fn)
            return self

        return decorator

    def register(
        self, condition: Callable[..., bool] = _always_true, priority: int = 0
    ) -> Decorator:
        def decorator[**P, T](fn: Callable[P, T]) -> Callable[P, T]:
            bisect.insort(
                self.registry,
                Function(condition=condition, function=fn, priority=priority),
                key=operator.attrgetter("priority"),
            )
            functools.update_wrapper(self, fn)
            return self

        return decorator
