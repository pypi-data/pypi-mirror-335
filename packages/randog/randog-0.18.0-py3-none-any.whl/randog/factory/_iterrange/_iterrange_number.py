import numbers
import typing as t

from ._inner import Iterrange


class IterrangeNumber(Iterrange[numbers.Real, numbers.Real]):
    def step_sign(self) -> t.Literal[-1, 0, 1]:
        if self._step > 0:
            return 1
        elif self._step < 0:
            return -1
        else:
            return 0

    def default_initial_value(self) -> numbers.Real:
        return 1

    def default_step(self) -> numbers.Real:
        return 1
