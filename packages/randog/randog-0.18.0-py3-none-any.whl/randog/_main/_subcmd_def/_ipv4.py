import argparse
import ipaddress
import sys
import typing as t

import randog.factory
from ..._utils.type import ipv4_network
from ..._processmode import Subcmd
from .. import Args
from ._base import SubcmdDef, add_common_arguments
from .._rnd import construct_random


class SubcmdDefIPV4(SubcmdDef):
    def cmd(self) -> Subcmd:
        return Subcmd.IPV4

    def add_parser(self, subparsers) -> argparse.ArgumentParser:
        ipv4_parser = subparsers.add_parser(
            Subcmd.IPV4.value,
            usage="randog ipv4 [NETWORK...] [--fmt FORMAT] [common-options]",
            description="It generates values of type IPv4Address.",
            add_help=False,
        )
        ipv4_args_group = ipv4_parser.add_argument_group("arguments")
        ipv4_args_group.add_argument(
            "network",
            type=ipv4_network,
            nargs="*",
            default=None,
            metavar="NETWORK",
            help="the network(s) which contain generated IP addresses.",
        )
        ipv4_args_group.add_argument(
            "--fmt",
            dest="format",
            metavar="FORMAT",
            help=(
                "if specified, it outputs generated value with the specified format, "
                "such as '#b'. It can use ONLY in python>=3.9.0"
            ),
        )
        add_common_arguments(ipv4_parser)

        return ipv4_parser

    def _validate_parser(self, args: Args, subparser: argparse.ArgumentParser):
        if args.format is not None and sys.version_info < (3, 9):
            subparser.error(
                "argument --fmt: python>=3.9.0 is required to use --fmt for ipv4"
            )

    def build_args(
        self, args: Args
    ) -> t.Tuple[t.Sequence[t.Any], t.Mapping[str, t.Any]]:
        network_str = args.get("network")
        rnd = construct_random(args.seed)
        kwargs = {
            "network": (
                tuple(ipaddress.IPv4Network(v) for v in network_str)
                if len(network_str) > 0
                else None
            ),
            "rnd": rnd,
        }

        return tuple(), kwargs

    def get_factory_constructor(self) -> t.Callable:
        return randog.factory.randipv4
