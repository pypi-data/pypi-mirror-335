import argparse
import typing as t

import randog.factory
from ..._processmode import Subcmd
from .. import Args
from ._base import SubcmdDef, add_common_arguments
from .._rnd import construct_random
from ..._utils.type import dice_roll
from ...exceptions import FactoryConstructionError
from ...factory import parse_dice_notation


class SubcmdDefDice(SubcmdDef):
    def cmd(self) -> Subcmd:
        return Subcmd.Dice

    def add_parser(self, subparsers) -> argparse.ArgumentParser:
        dice_parser = subparsers.add_parser(
            Subcmd.Dice.value,
            usage="randog dice DICE_ROLL [common-options]",
            description="It generates integer values as total of the dice faces.",
            add_help=False,
        )
        dice_args_group = dice_parser.add_argument_group("arguments")
        dice_args_group.add_argument(
            "code",
            type=dice_roll,
            metavar="DICE_ROLL",
            help="the dice notation",
        )
        add_common_arguments(dice_parser)

        return dice_parser

    def _validate_parser(self, args: Args, subparser: argparse.ArgumentParser):
        iargs, kwargs = self.build_args(args)
        code = iargs[0]

        try:
            parse_dice_notation(code)
        except FactoryConstructionError as e:
            subparser.error(e.message)

    def build_args(
        self, args: Args
    ) -> t.Tuple[t.Sequence[t.Any], t.Mapping[str, t.Any]]:
        rnd = construct_random(args.seed)
        return (args.get("code"),), {
            "rnd": rnd,
        }

    def get_factory_constructor(self) -> t.Callable:
        return randog.factory.dice
