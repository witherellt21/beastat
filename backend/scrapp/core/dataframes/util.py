from typing import Iterable, Union

import pandas as pd


def safe_concat(df1: pd.DataFrame, df2: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    return (
        df1.copy()
        if df2.empty
        else (
            df2.copy() if df1.empty else pd.concat([df1, df2], *args, **kwargs)
        )  # if both DataFrames non empty
    )


def safe_set_column(
    df: pd.DataFrame,
    column: str,
    value: Union[str, int, float, pd.Series, pd.DataFrame],
):
    if isinstance(value, pd.DataFrame):
        df = safe_concat(df, value)
    else:
        df[column] = value

    return df
