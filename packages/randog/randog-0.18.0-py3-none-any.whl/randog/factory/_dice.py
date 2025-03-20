import re
import typing as t
from random import Random

from ._base import Factory, decide_rnd
from ._int import randint
from ..exceptions import FactoryConstructionError

_RE_DICE_NOTATION = re.compile("([0-9]*)[dD]([0-9]+)")


def parse_dice_notation(
    code: str,
    *,
    exception: t.Type[Exception] = ValueError,
) -> t.Tuple[int, int]:
    code_match = re.fullmatch(_RE_DICE_NOTATION, code)
    if code_match is None:
        raise exception(f"invalid dice notation: {code}")

    dice_num = int(code_match.group(1) or "1")
    dice_max = int(code_match.group(2))

    if dice_num <= 0:
        raise exception(
            f"invalid dice notation; the number of dice must be at least 1: {code}"
        )
    if dice_max <= 0:
        raise exception(
            f"invalid dice notation; the number of faces on the dice must be at "
            f"least 1: {code}"
        )

    return dice_num, dice_max


def dice(
    code: str,
    *,
    rnd: t.Optional[Random] = None,
) -> Factory[int]:
    """Return a factory generating random int values by total of the dice faces.

    Parameters
    ----------
    code : str
        dice notation
    rnd : Random, optional
        random number generator to be used

    Raises
    ------
    FactoryConstructionError
        When the specified code is invalid.
    """
    return DiceRandomFactory(code, rnd=rnd)


class DiceRandomFactory(Factory[int]):
    """factory generating random int values by total of the dice faces."""

    _random: Random
    _base_factory: Factory[int]
    _dice_num: int

    def __init__(
        self,
        code: str,
        *,
        rnd: t.Optional[Random] = None,
    ):
        """Return a factory generating random int values by total of the dice faces.

        Parameters
        ----------
        code : str
            dice notation
        rnd : Random, optional
            random number generator to be used

        Raises
        ------
        FactoryConstructionError
            When the specified code is invalid.
        """
        self._random = decide_rnd(rnd)

        self._dice_num, dice_max = parse_dice_notation(
            code, exception=FactoryConstructionError
        )

        self._base_factory = randint(1, dice_max, rnd=self._random)

    def _next(self) -> int:
        return sum(self._base_factory.iter(self._dice_num))
