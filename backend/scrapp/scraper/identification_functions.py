from typing import Callable, Optional

import pandas as pd


def indexed(index: int) -> Callable[[list[pd.DataFrame]], Optional[pd.DataFrame]]:
    def func(tables: list[pd.DataFrame]):
        if len(tables) < index + 1:
            return None

        return tables[index]

    return func
