import numpy as np


def strppct(pct: str) -> int | float:
    if not isinstance(pct, str):
        raise TypeError(
            f"'pct' must be of type 'str'; got '{pct.__class__.__name__}' = {pct}."
        )

    val = pct.strip("%")

    try:
        as_float = float(val)
    except ValueError:
        return np.nan

    as_int = int(as_float)

    return as_float if as_float != as_int else as_int


def strfpct(pct: int | float):
    # TODO
    pass
