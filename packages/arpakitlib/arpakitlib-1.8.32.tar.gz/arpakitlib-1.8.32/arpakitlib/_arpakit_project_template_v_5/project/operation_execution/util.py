from datetime import timedelta, time
from typing import Callable

from arpakitlib.ar_datetime_util import now_utc_dt


def every_timedelta_is_time_func(*, td: timedelta, now_dt_func: Callable = now_utc_dt) -> Callable:
    last_now_utc_dt = now_utc_dt()

    def func() -> bool:
        nonlocal last_now_utc_dt
        now_dt_func_ = now_dt_func()
        if (now_dt_func_ - last_now_utc_dt) >= td:
            last_now_utc_dt = now_dt_func_
            return True
        return False

    return func


def between_different_times_is_time_func(
        *, from_time: time, to_time: time, now_dt_func: Callable = now_utc_dt
) -> Callable:
    def func() -> bool:
        if from_time <= now_dt_func().time() <= to_time:
            return True
        return False

    return func
