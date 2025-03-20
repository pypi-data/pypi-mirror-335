import codecs
import dataclasses
import random
import types
import typing as t
from os import PathLike

from .._utils.linesep import Linesep
from randog.factory import Factory


@dataclasses.dataclass
class FactoryDef:
    factory: Factory
    csv_columns: t.Optional[t.Sequence[t.Union[str, t.Callable[[t.Mapping], t.Any]]]]
    output_linesep: t.Optional[Linesep]
    output_encoding: t.Optional[str]


@t.overload
def from_pyfile(
    file: t.Union[str, PathLike, t.IO],
    *,
    full_response: t.Literal[False] = False,
    rnd: t.Optional[random.Random] = None,
) -> Factory:
    pass


@t.overload
def from_pyfile(
    file: t.Union[str, PathLike, t.IO],
    *,
    full_response: t.Literal[True],
    rnd: t.Optional[random.Random] = None,
) -> FactoryDef:
    pass


def from_pyfile(
    file: t.Union[str, PathLike, t.IO],
    *,
    full_response: bool = False,
    rnd: t.Optional[random.Random] = None,
) -> t.Union[FactoryDef, Factory]:
    """Returns a factory defined in the specified file.

    Parameters
    ----------
    file : str | PathLike | IO
        the filename of the factory definition
    full_response : bool (default=False)
        If True is specified, the return value is the FactoryDef dataclass,
        and data other than the factory can be obtained.
    rnd : Random, optional
        random number generator to be used
    """
    if isinstance(file, (str, PathLike)):
        with open(file, mode="rb") as fp:
            factory_def = _from_pyfile(fp, file, rnd)
    else:
        factory_def = _from_pyfile(file, "<io>", rnd)

    if full_response:
        return factory_def
    else:
        return factory_def.factory


FACTORY_ATTR_NAME = "FACTORY"
CSV_COL_ATTR_NAME = "CSV_COLUMNS"
OUT_LINESEP_ATTR_NAME = "OUTPUT_LINESEP"
OUT_ENCODING_ATTR_NAME = "OUTPUT_ENCODING"


def _from_pyfile(
    fp: t.IO,
    filename: t.Union[str, PathLike],
    rnd: t.Optional[random.Random],
) -> FactoryDef:
    import randog
    from . import _from_pyfile_config

    d = types.ModuleType("__randog__")
    d.__file__ = str(filename)
    d.randog = randog
    origin_from_pyfile_config_rnd = _from_pyfile_config.rnd
    if rnd is not None:
        _from_pyfile_config.rnd = rnd

    try:
        exec(compile(fp.read(), filename, "exec"), d.__dict__)
    except OSError as e:
        e.strerror = f"Unable to load factory file ({e.strerror})"
        raise
    finally:
        _from_pyfile_config.rnd = origin_from_pyfile_config_rnd

    return _load_factory_module(d, filename=filename)


def _load_factory_module(
    module: types.ModuleType, *, filename: t.Union[str, PathLike]
) -> FactoryDef:
    if not hasattr(module, FACTORY_ATTR_NAME):
        raise AttributeError(
            f"factory file '{filename}' has no attribute '{FACTORY_ATTR_NAME}'"
        )

    factory = getattr(module, FACTORY_ATTR_NAME)
    if not isinstance(factory, Factory):
        raise AttributeError(
            f"attribute '{FACTORY_ATTR_NAME}' "
            f"of factory file '{filename}' is not a factory"
        )

    csv_columns = getattr(module, CSV_COL_ATTR_NAME, None)
    if csv_columns is not None and not isinstance(csv_columns, t.Sequence):
        raise AttributeError(
            f"attribute '{CSV_COL_ATTR_NAME}' "
            f"of factory file '{filename}' MUST be None or a sequence of strings"
        )

    output_linesep_str = getattr(module, OUT_LINESEP_ATTR_NAME, None)
    try:
        output_linesep = (
            Linesep.of(output_linesep_str) if output_linesep_str is not None else None
        )
    except ValueError:
        raise AttributeError(
            f"attribute '{OUT_LINESEP_ATTR_NAME}' "
            f"of factory file '{filename}' MUST be None or "
            f"{', '.join(v.name for v in Linesep)}"
        )

    output_encoding = getattr(module, OUT_ENCODING_ATTR_NAME, None)
    if output_encoding is not None:
        if not isinstance(output_encoding, str):
            raise AttributeError(
                f"attribute '{OUT_ENCODING_ATTR_NAME}' "
                f"of factory file '{filename}' MUST be None or an encoding string"
            )
        try:
            codecs.lookup(output_encoding)
        except LookupError:
            raise AttributeError(
                f"attribute '{OUT_ENCODING_ATTR_NAME}' "
                f"of factory file '{filename}' MUST be None or an encoding string"
            )

    return FactoryDef(
        factory=factory,
        csv_columns=csv_columns,
        output_linesep=output_linesep,
        output_encoding=output_encoding,
    )
