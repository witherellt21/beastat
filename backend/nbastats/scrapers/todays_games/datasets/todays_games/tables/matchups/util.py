import pandas as pd


def has_position_column(tables: list[pd.DataFrame]):
    data = next(
        (table for table in tables if "position" in table.columns),
        None,
    )
    return data
