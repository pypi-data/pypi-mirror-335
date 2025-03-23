from collections.abc import Callable
from typing import Protocol


class Decorator(Protocol):
    def __call__[**P, T](self, fn: Callable[P, T]) -> Callable[P, T]: ...
