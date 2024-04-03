from typing import Type, Union

import numpy as np
import pandas as pd


def sum_nullables(*args, type: Type[Union[int, float]] = float):
    total: type = 0
    valid = False
    for arg in args:
        if arg != np.nan:
            valid = True
            total += type(arg)

    return total if valid else np.nan
