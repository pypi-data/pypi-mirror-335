import datetime as dt
import typing as t

from ._inner import Iterrange
from ...exceptions import FactoryConstructionError


class IterrangeDate(Iterrange[dt.date, dt.timedelta]):
    def default_initial_value(self) -> dt.date:
        return dt.date(1970, 1, 1)

    def default_step(self) -> dt.timedelta:
        return dt.timedelta(days=1)

    def step_sign(self) -> t.Literal[-1, 0, 1]:
        value = self._step.total_seconds()
        if value > 0:
            return 1
        elif value < 0:
            return -1
        else:
            return 0

    def validate_args(self, **kwargs):
        super().validate_args(**kwargs)

        if self._step.microseconds + self._step.seconds > 0:
            raise FactoryConstructionError(
                "step must be a day/days if initial_value is date"
            )
