import enum
import typing as t


class Linesep(enum.Enum):
    LF = "\n"
    CRLF = "\r\n"
    CR = "\r"

    @classmethod
    def names(cls) -> t.Tuple[str, ...]:
        return tuple(map(lambda e: e.name, cls))

    @classmethod
    def of(cls, value: str) -> "Linesep":
        try:
            return _LINESEP_MAP[value]
        except KeyError as e:
            raise ValueError(e)


_LINESEP_MAP = {**{v.name: v for v in Linesep}, **{v.value: v for v in Linesep}}
