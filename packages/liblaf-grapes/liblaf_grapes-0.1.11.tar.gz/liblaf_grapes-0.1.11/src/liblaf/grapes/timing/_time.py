import os
import time
from typing import Literal

import autoregistry

type TimeCounterName = Literal[
    "children_system",
    "children_user",
    "elapsed",
    "monotonic",
    "perf",
    "process",
    "system",
    "thread",
    "time",
    "user",
]


REGISTRY = autoregistry.Registry()
REGISTRY["children_system"] = lambda: os.times().children_system
REGISTRY["children_user"] = lambda: os.times().children_user
REGISTRY["elapsed"] = lambda: os.times().elapsed
REGISTRY["monotonic"] = time.monotonic
REGISTRY["perf"] = time.perf_counter
REGISTRY["process"] = time.process_time
REGISTRY["system"] = lambda: os.times().system
REGISTRY["thread"] = time.thread_time
REGISTRY["time"] = time.time
REGISTRY["user"] = lambda: os.times().user


def get_time(name: TimeCounterName | str = "perf") -> float:
    """Retrieve the current time from the specified time counter.

    Args:
        name: The name of the time counter to use.

    Returns:
        The current time from the specified time counter.
    """
    return REGISTRY[name]()
