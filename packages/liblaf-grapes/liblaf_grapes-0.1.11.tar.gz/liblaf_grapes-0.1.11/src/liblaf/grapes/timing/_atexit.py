import atexit

from . import TimerRecordsTrait

TIMERS: list[TimerRecordsTrait] = []


def register_timer(timer: TimerRecordsTrait) -> None:
    TIMERS.append(timer)


def log_summary() -> None:
    for timer in TIMERS:
        if timer.log_summary_at_exit and timer.n_rows > 1:
            timer.log_summary()


atexit.register(log_summary)
