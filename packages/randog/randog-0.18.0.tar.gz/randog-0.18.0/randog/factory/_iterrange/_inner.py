import abc
import inspect
import typing as t
from random import Random

from .._logging import logger
from ..._utils.comp import ANYWAY_MAXIMUM, ANYWAY_MINIMUM
from .._base import Factory, T as F_T
from ...exceptions import FactoryConstructionError

S = t.TypeVar("S")


class Iterrange(Factory[F_T], abc.ABC, t.Generic[F_T, S]):
    _initial_value: F_T
    _minimum: F_T
    _maximum: F_T
    _step: S
    _cyclic: bool
    _resume_value: F_T
    _impl_iterator: t.Iterator[F_T]

    def __init__(
        self,
        initial_value: F_T,
        maximum: t.Optional[F_T],
        step: t.Optional[S],
        cyclic: bool,
        resume_from: t.Optional[F_T],
        rnd: t.Optional[Random] = None,
    ):
        if initial_value is not None:
            self._initial_value = initial_value
        else:
            self._initial_value = self.default_initial_value()
        if step is not None:
            self._step = step
        else:
            self._step = self.default_step()
        self._cyclic = cyclic

        if self.step_sign() < 0:
            minimum = maximum
            maximum = None
        else:
            minimum = None
        if maximum is None:
            maximum = ANYWAY_MAXIMUM
        if minimum is None:
            minimum = ANYWAY_MINIMUM
        self._minimum = minimum
        self._maximum = maximum

        self._resume_value = (
            resume_from if resume_from is not None else self._initial_value
        )

        arg_info = inspect.getargvalues(inspect.currentframe())
        self.validate_args(**{key: arg_info.locals[key] for key in arg_info.args[1:]})

        self._impl_iterator = self._iterator()

    @abc.abstractmethod
    def default_initial_value(self) -> F_T:
        pass

    @abc.abstractmethod
    def default_step(self) -> S:
        pass

    @abc.abstractmethod
    def step_sign(self) -> t.Literal[-1, 0, 1]:
        pass

    def validate_args(self, **kwargs):
        if not self._cyclic and kwargs["resume_from"] is not None:
            raise FactoryConstructionError(
                "cannot specify 'resume_from' with cyclic=False"
            )

        if self.step_sign() >= 0:
            if not (self._initial_value <= self._maximum):
                raise FactoryConstructionError(
                    "arguments of iterrange() must satisfy initial_value <= maximum"
                )
            if not (self._resume_value <= self._maximum):
                raise FactoryConstructionError(
                    "arguments of iterrange() must satisfy resume_from <= maximum "
                    "if resume_from is specified"
                )
        else:
            if not (self._initial_value >= self._minimum):
                raise FactoryConstructionError(
                    "arguments of iterrange() must satisfy "
                    "maximum <= initial_value if step < 0"
                )
            if not (self._resume_value >= self._minimum):
                raise FactoryConstructionError(
                    "arguments of iterrange() must satisfy "
                    "maximum <= resume_from if resume_from is specified and step < 0"
                )

    def _next(self) -> F_T:
        return next(self._impl_iterator)

    def _iterator(self) -> t.Iterator[F_T]:
        next_value = self._initial_value
        while True:
            yield next_value
            next_value += self._step

            if next_value > self._maximum or next_value < self._minimum:
                if self._cyclic:
                    logger.debug(
                        "iterrange() has reached its maximum value and resumes "
                        f"from {self._resume_value}"
                    )
                    next_value = self._resume_value
                else:
                    logger.debug(
                        "iterrange() has reached its maximum value. "
                        "This factory no longer generates values."
                    )
                    break
