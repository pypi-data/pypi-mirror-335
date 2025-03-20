import datetime as dt
import typing as t

from ._inner import Iterrange


class IterrangeDatetime(Iterrange[dt.datetime, dt.timedelta]):
    def default_initial_value(self) -> dt.datetime:
        return dt.datetime(1970, 1, 1)

    def default_step(self) -> dt.timedelta:
        return dt.timedelta(seconds=1)

    def step_sign(self) -> t.Literal[-1, 0, 1]:
        value = self._step.total_seconds()
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return 0
