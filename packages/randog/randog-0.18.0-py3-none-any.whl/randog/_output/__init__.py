import csv
import os
import sys
import typing as t
import warnings

from .._processmode import get_process_mode, Subcmd
from ..exceptions import RandogWarning
from ..factory import Factory


def generate_to_csv(
    factory: Factory,
    line_num: int,
    fp: t.TextIO,
    csv_columns: t.Optional[t.Sequence[t.Union[str, t.Callable[[t.Mapping], t.Any]]]],
    *,
    regenerate: float = 0.0,
    discard: float = 0.0,
    raise_on_factory_stopped: bool = False,
    linesep: t.Optional[str] = None,
):
    """Generate values randomly and output as CSV

    Parameters
    ----------
    factory : Factory
        the factory to generate values
    line_num : int
        the number of the iterator.
        However, if the argument `raise_on_factory_stopped` is not True,
        fewer iterations than the specified `size` will be executed
        if the factory is stopped.
        Also, if the argument `discard` is specified, the size may be less.
    fp : TextIO
        CSV output destination
    csv_columns : list[str, Callable[[Mapping], Any]] | None
        the definitions of each column value.
        If it is defined with str,
        the value is taken from the generated object using that as the key.
        If it is defined with a function,
        the function is used with the generated object as an argument,
        and the return value is used.
    regenerate : float, default=0.0
        the probability that the original factory generation value is not returned
        as is, but is regenerated.
        It affects cases where the original factory returns a value
        that is not completely random.
    discard : float, default=0.0
        the probability that the original factory generation value is not returned
        as is, but is discarded.
        If discarded, the number of times the value is generated is less than
        `size`.
    raise_on_factory_stopped : bool, default=False
        If True, raises `FactoryStopException`
        in case the factory cannot generate value due to `StopIteration`.
        If False, simply raises `StopIteration`.
    linesep : str, optional
        If specified, CSV rows are separated by this string.
    """
    writer_options = {}
    if fp in (sys.stdout, sys.stderr):
        # windows で "\r\n" にすると、標準出力時に改行が "\r\r\n" に変換されてしまう。
        # よって、windows で改行を "\r\n" にしたい場合も、標準出力時はここには　"\n" を指定する。
        writer_options["lineterminator"] = "\n"
    elif linesep is None:
        writer_options["lineterminator"] = os.linesep
    else:
        writer_options["lineterminator"] = linesep

    csv_writer = csv.writer(fp, **writer_options)
    csv_writer.writerows(
        filter(
            lambda x: x is not None,
            factory.post_process(_create_csv_row_post_function(csv_columns)).iter(
                line_num,
                regenerate=regenerate,
                discard=discard,
                raise_on_factory_stopped=raise_on_factory_stopped,
            ),
        )
    )


def _get_csv_field(
    pre_value: t.Mapping,
    col: t.Union[str, t.Callable[[t.Mapping], t.Any]],
) -> t.Any:
    if isinstance(col, t.Callable):
        return col(pre_value)
    else:
        return pre_value.get(col)


def _create_csv_row_post_function(
    csv_columns: t.Optional[t.Sequence[t.Union[str, t.Callable[[t.Mapping], t.Any]]]],
):
    if csv_columns is not None:

        def _post_function(pre_value) -> t.Optional[t.Sequence[t.Any]]:
            if pre_value is None:
                return None
            elif isinstance(pre_value, t.Mapping):
                return [_get_csv_field(pre_value, col) for col in csv_columns]
            elif isinstance(pre_value, t.Sequence) and not isinstance(pre_value, str):
                return pre_value
            else:
                # different warnings depending on the mode of the process
                if get_process_mode() is not None:
                    warnings.warn(
                        "--csv is recommended for only collections (such as "
                        "dict, list, tuple, etc.); "
                        "In CSV output, one generated value is treated as one row, "
                        "so the result is the same as --repeat except for collections; "
                        "CSV_COLUMNS in the definition file is ignored.",
                        RandogWarning,
                    )
                else:
                    warnings.warn(
                        "CSV output is recommended for only collections "
                        "(such as dict, list, tuple, etc.); "
                        "In CSV output, one generated value is treated as one row, "
                        "so the result is the same as iteration of "
                        "'print(factory.next())'; "
                        "csv_columns specified as argument is ignored.",
                        RandogWarning,
                    )
                return [pre_value]

    else:

        def _post_function(pre_value) -> t.Optional[t.Sequence[t.Any]]:
            if pre_value is None:
                return None
            elif isinstance(pre_value, t.Mapping):
                # different warnings depending on the mode of the process
                p_mode = get_process_mode()
                if p_mode is not None:
                    # Why msg_part is defined:
                    #   Consider the possibility that future modifications will allow
                    #   users to reach here in other than byfile mode,
                    #   and branch the error message.
                    msg_part = (
                        " in the definition file" if p_mode is Subcmd.Byfile else ""
                    )
                    warnings.warn(
                        f"Since CSV_COLUMNS is not defined{msg_part}, "
                        "the fields are inserted in the order returned by the "
                        "dictionary; In this case, fields may not be aligned "
                        "depending on the FACTORY definition, "
                        "so it is recommended to define CSV_COLUMNS.",
                        RandogWarning,
                    )
                else:
                    warnings.warn(
                        "Since csv_columns is None, "
                        "the fields are inserted in the order returned by the "
                        "dictionary; In this case, fields may not be aligned "
                        "depending on the factory definition, "
                        "so it is recommended to specify non-none csv_columns.",
                        RandogWarning,
                    )
                return list(pre_value.values())
            elif isinstance(pre_value, t.Sequence) and not isinstance(pre_value, str):
                return pre_value
            else:
                # different warnings depending on the mode of the process
                if get_process_mode() is not None:
                    warnings.warn(
                        "--csv is recommended for only collections (such as "
                        "dict, list, tuple, etc.); "
                        "In CSV output, one generated value is treated as one row, "
                        "so the result is the same as --repeat except for collections.",
                        RandogWarning,
                    )
                else:
                    warnings.warn(
                        "CSV output is recommended for only collections "
                        "(such as dict, list, tuple, etc.); "
                        "In CSV output, one generated value is treated as one row, "
                        "so the result is the same as iteration of "
                        "'print(factory.next())'.",
                        RandogWarning,
                    )
                return [pre_value]

    return _post_function
