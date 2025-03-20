import datetime as dt
import numbers
import typing as t
from random import Random

from ._iterrange_date import IterrangeDate
from ._iterrange_datetime import IterrangeDatetime
from ._iterrange_number import IterrangeNumber
from ._iterrange_timedelta import IterrangeTimedelta
from .._base import Factory


@t.overload
def iterrange(
    initial_value: t.Optional[int] = None,
    maximum: t.Optional[int] = None,
    step: t.Optional[int] = None,
    *,
    cyclic: bool = False,
    resume_from: t.Optional[t.Any] = None,
    rnd: t.Optional[Random] = None,
) -> Factory[int]: ...


@t.overload
def iterrange(
    initial_value: dt.datetime,
    maximum: t.Optional[dt.datetime] = None,
    step: t.Optional[dt.timedelta] = None,
    *,
    cyclic: bool = False,
    resume_from: t.Optional[t.Any] = None,
    rnd: t.Optional[Random] = None,
) -> Factory[dt.datetime]: ...


@t.overload
def iterrange(
    initial_value: dt.date,
    maximum: t.Optional[dt.date] = None,
    step: t.Optional[dt.timedelta] = None,
    *,
    cyclic: bool = False,
    resume_from: t.Optional[t.Any] = None,
    rnd: t.Optional[Random] = None,
) -> Factory[dt.date]: ...


@t.overload
def iterrange(
    initial_value: dt.timedelta,
    maximum: t.Optional[dt.timedelta] = None,
    step: t.Optional[dt.timedelta] = None,
    *,
    cyclic: bool = False,
    resume_from: t.Optional[t.Any] = None,
    rnd: t.Optional[Random] = None,
) -> Factory[dt.timedelta]: ...


def iterrange(
    initial_value: t.Optional[t.Any] = None,
    maximum: t.Optional[t.Any] = None,
    step: t.Optional[t.Any] = None,
    *,
    cyclic: bool = False,
    resume_from: t.Optional[t.Any] = None,
    rnd: t.Optional[Random] = None,
) -> Factory[t.Any]:
    """Return a factory which returns sequential numbers.

    This is a factory that generates values that are shifted by the value specified in
    step from `initial_value`.

    If you specify maximum, it will emit StopIterator when a value that exceeds it is
    about to be generated. However, if cyclic is True, it will not emit StopIterator,
    but will restart generating from initial_value.

    Parameters
    ----------
    initial_value
        the first value
    maximum : optional
        the maximum value
    step : optional
        difference between generated values
    cyclic : bool
        If it is True, it does not terminate after generating values up to the maximum.
        The next value depends on the other arguments;
        by default initial_value is returned.
    resume_from : optional
        If cyclic is True and this value is specified,
        the value specified here is the next value after maximum.
    rnd : Random, optional
        It is not normally used, but it can be accepted as an argument
        to match other Factory construction functions.

    Raises
    ------
    FactoryConstructionError
        if there is a contradiction in the argument values
    """
    if initial_value is None or isinstance(initial_value, numbers.Real):
        return IterrangeNumber(
            initial_value,
            maximum,
            step,
            cyclic=cyclic,
            resume_from=resume_from,
            rnd=rnd,
        )
    elif isinstance(initial_value, dt.datetime):
        return IterrangeDatetime(
            initial_value,
            maximum,
            step,
            cyclic=cyclic,
            resume_from=resume_from,
            rnd=rnd,
        )
    elif isinstance(initial_value, dt.date):
        return IterrangeDate(
            initial_value,
            maximum,
            step,
            cyclic=cyclic,
            resume_from=resume_from,
            rnd=rnd,
        )
    elif isinstance(initial_value, dt.timedelta):
        return IterrangeTimedelta(
            initial_value,
            maximum,
            step,
            cyclic=cyclic,
            resume_from=resume_from,
            rnd=rnd,
        )
    else:
        raise TypeError(
            "cannot create 'iterrange' factory with initial_value "
            f"type of {type(initial_value)}"
        )
