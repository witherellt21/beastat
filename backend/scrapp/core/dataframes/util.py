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


def splinter_dataframe(
    df: pd.DataFrame, n: int, *, index: None | str | list[str] | tuple[str, ...] = None
):
    if index:
        df = df.set_index(index)

    columns = df.columns.to_list()

    col_splints = [columns[i : i + n] for i in range(0, len(columns), n)]

    tables: list[pd.DataFrame] = []
    for col_splint in col_splints:
        tables.append(df[col_splint])

    return tables


def print_df(
    df: pd.DataFrame,
    width: int = 10,
    splint_index: None | str | list[str] | tuple[str, ...] = None,
):
    tables = splinter_dataframe(df, width, index=splint_index)

    for table in tables:
        print(table)
