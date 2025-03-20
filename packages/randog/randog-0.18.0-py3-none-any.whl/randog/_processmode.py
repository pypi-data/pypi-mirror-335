from enum import Enum
import os
import typing as t

ENV_PROCESS_MODE = "RANDOG_PROCESS_MODE"


class Subcmd(Enum):
    Byfile = "byfile"
    Bool = "bool"
    Int = "int"
    Dice = "dice"
    Float = "float"
    String = "str"
    Decimal = "decimal"
    Datetime = "datetime"
    Date = "date"
    Time = "time"
    Timedelta = "timedelta"
    IPV4 = "ipv4"


def set_process_mode(mode: t.Optional[Subcmd]):
    if mode is not None:
        os.environ[ENV_PROCESS_MODE] = str(mode.value)
    else:
        del os.environ[ENV_PROCESS_MODE]


def get_process_mode() -> t.Optional[Subcmd]:
    mode_str = os.environ.get(ENV_PROCESS_MODE)
    return Subcmd(mode_str) if mode_str is not None else None
