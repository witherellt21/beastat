import pandas as pd
import pytest
from lib.dataframes import (
    augment_dataframe,
    filter_dataframe,
    filter_with_bounds,
    reorder_columns,
)


@pytest.mark.parametrize(
    "dataframe, column_order, expected_order",
    (
        (
            pd.DataFrame({"PTS": [1, 2, 3], "REB": [5, 3, 4], "COL": [None, 2, ""]}),
            ["COL", "REB"],
            ["COL", "REB", "PTS"],
        ),
        (
            pd.DataFrame({"PTS": [1, 2, 3], "REB": [5, 3, 4], "COL": [None, 2, ""]}),
            ["COL", "DNE"],
            ["COL", "PTS", "REB"],
        ),
    ),
)
def test_reorder_columns(
    dataframe: pd.DataFrame, column_order: list[str], expected_order: list[str]
):
    reordered = reorder_columns(dataframe, column_order)

    assert list(reordered.columns) == expected_order
