import ipaddress
import typing as t
from random import Random

from ._base import Factory, decide_rnd
from ._int import randint
from ._union import union
from ..exceptions import FactoryConstructionError


def randipv4(
    network: t.Union[
        ipaddress.IPv4Network, t.Iterable[ipaddress.IPv4Network], None
    ] = None,
    *,
    rnd: t.Optional[Random] = None,
) -> Factory[ipaddress.IPv4Address]:
    """Return a factory generating random int values.

    Parameters
    ----------
    network : IPv4Network | Iterable[IPv4Network]
        address space that is a candidate for the generated IP address
    rnd : Random, optional
        random number generator to be used

    Raises
    ------
    FactoryConstructionError
        When the specified generating conditions are inconsistent.
    """
    return Ipv4RandomFactory(network, rnd=rnd)


def _network_to_range(network: ipaddress.IPv4Network) -> t.Tuple[int, int, int]:
    """returns start, end, and weight

    The range of values returned by hosts() is used as the range of values to generate.
    """
    if network.num_addresses == 1:
        address_int = int(network.network_address)
        return address_int, address_int, 1
    elif network.num_addresses == 2:
        return int(network.network_address), int(network.broadcast_address), 2
    else:
        return (
            int(network.network_address) + 1,
            int(network.broadcast_address) - 1,
            network.num_addresses - 2,
        )


class Ipv4RandomFactory(Factory[ipaddress.IPv4Address]):
    """factory generating random IPv4Address values"""

    _random: Random
    _networks: t.Optional[t.Sequence[ipaddress.IPv4Network]]
    _factory: Factory[int]

    def __init__(
        self,
        network: t.Union[
            ipaddress.IPv4Network, t.Iterable[ipaddress.IPv4Network], None
        ],
        *,
        rnd: t.Optional[Random] = None,
    ):
        """Return a factory generating random int values.

        Parameters
        ----------
        network : IPv4Network | Iterable[IPv4Network]
            address space that is a candidate for the generated IP address
        rnd : Random, optional
            random number generator to be used

        Raises
        ------
        FactoryConstructionError
            When the specified generating conditions are inconsistent.
        """
        self._random = decide_rnd(rnd)

        if network is None:
            self._networks = None
        elif isinstance(network, ipaddress.IPv4Network):
            self._networks = [network]
        else:
            self._networks = list(network)
        if self._networks is not None and len(self._networks) <= 0:
            raise FactoryConstructionError("empty address space for randipv4")

        ranges = (
            [_network_to_range(net) for net in self._networks]
            if self._networks is not None
            else _DEFAULT_NETWORK_RANGES
        )
        child_factories = [
            randint(minimum, maximum, rnd=rnd) for minimum, maximum, _ in ranges
        ]
        weights = [w for _, _, w in ranges]

        self._factory = union(*child_factories, weights=weights, rnd=rnd)

    def _next(self) -> ipaddress.IPv4Address:
        return ipaddress.ip_address(self._factory.next())


_DEFAULT_NETWORK_RANGES = (_network_to_range(ipaddress.IPv4Network("192.0.2.0/24")),)
