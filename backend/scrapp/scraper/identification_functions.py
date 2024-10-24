from typing import Optional

import pandas as pd


def first(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
    return tables[0]
