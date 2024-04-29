from datetime import date
from typing import Any, Callable, Mapping

import pandas as pd
import pytest
from lib.dataframes import augment_dataframe, filter_dataframe, filter_with_bounds


@pytest.mark.parametrize(
    "dataframe, filters, expected",
    (
        (
            pd.DataFrame({"PTS": [1, 5, 10], "REB": [4, 5, 9]}),
            [lambda x: x["PTS"] >= 5, lambda x: x["REB"] >= 6],
            pd.DataFrame({"PTS": [10], "REB": [9]}),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 10], "REB": [4, 5, 9]}),
            [lambda x: x["PTS"] >= 0, lambda x: x["PTS"] >= 5],
            pd.DataFrame({"PTS": [5, 10], "REB": [5, 9]}),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 10], "REB": [4, 5, 9]}),
            [lambda x: x["PTS"] >= 0, lambda x: x["PTS"] >= 5],
            pd.DataFrame({"PTS": [5, 10], "REB": [5, 9]}),
        ),
    ),
)
def test_filter_dataframe(
    dataframe: pd.DataFrame, filters: list[Callable], expected: pd.DataFrame
):
    filtered = filter_dataframe(dataframe, filters)

    assert filtered.equals(expected)


@pytest.mark.parametrize(
    "dataframe, filters, expected",
    (
        (
            pd.DataFrame({"PTS": [1, 5, 10], "REB": [4, 5, 9]}),
            [lambda x: x["PTS"], lambda x: x["PTS"] >= 5],
            pd.DataFrame({"PTS": [5, 10], "REB": [5, 9]}),
        ),
    ),
)
def test_filter_dataframe_nonboolean_filter_raises_value_error(
    dataframe: pd.DataFrame, filters: list[Callable], expected: pd.DataFrame
):
    with pytest.raises(ValueError) as error:
        filtered = filter_dataframe(dataframe, filters)


@pytest.mark.parametrize(
    "dataframe, filters, expected",
    (
        (
            pd.DataFrame({"PTS": [1, 5, 10], "REB": [4, 5, 9]}),
            [lambda x, y: x["PTS"] > 10],
            pd.DataFrame({"PTS": [5, 10], "REB": [5, 9]}),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 10], "REB": [4, 5, 9]}),
            [lambda: True],
            pd.DataFrame({"PTS": [5, 10], "REB": [5, 9]}),
        ),
    ),
)
def test_filter_dataframe_invalid_filter_arguments_raises_value_error(
    dataframe: pd.DataFrame, filters: list[Callable], expected: pd.DataFrame
):
    with pytest.raises(ValueError) as error:
        filtered = filter_dataframe(dataframe, filters)


@pytest.mark.parametrize(
    "dataframe, column, bounds, expected",
    (
        (
            pd.DataFrame({"PTS": [1, 5, 3, 6, 8], "REB": [5, 4, 2, 1, 7]}),
            "PTS",
            (3, 5),
            pd.DataFrame({"PTS": [5, 3], "REB": [4, 2]}, index=[1, 2]),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 3, 6, 8], "REB": [5, 4, 2, 1, 7]}),
            "PTS",
            (5, 3),
            pd.DataFrame({"PTS": [1, 6, 8], "REB": [5, 1, 7]}, index=[0, 3, 4]),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 3, 6, 8], "REB": [5, 4, 2, 1, 7]}),
            "PTS",
            (None, 3),
            pd.DataFrame({"PTS": [1, 3], "REB": [5, 2]}, index=[0, 2]),
        ),
        (
            pd.DataFrame(
                {
                    "Date": [
                        date(2020, 1, 1),
                        date(2020, 5, 1),
                        date(2020, 8, 1),
                    ],
                }
            ),
            "Date",
            (date(2020, 2, 1), None),
            pd.DataFrame(
                {
                    "Date": [
                        date(2020, 5, 1),
                        date(2020, 8, 1),
                    ]
                },
                index=[1, 2],
            ),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 3, 6, 8], "REB": [5, 4, 2, 1, 7]}),
            "PTS",
            (None, None),
            pd.DataFrame({"PTS": [1, 5, 3, 6, 8], "REB": [5, 4, 2, 1, 7]}),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 3, 6, 8], "REB": [5, 4, 2, 1, 7]}),
            "PTS",
            (3, 3),
            pd.DataFrame({"PTS": [3], "REB": [2]}, index=[2]),
        ),
    ),
)
def test_filter_with_bounds(
    dataframe: pd.DataFrame,
    column: str,
    bounds: tuple[Any, Any],
    expected: pd.DataFrame,
):
    result = filter_with_bounds(dataframe, column, bounds)

    assert result.equals(expected)


@pytest.mark.parametrize(
    "dataframe, augmentations, expected",
    (
        (
            pd.DataFrame({"PTS": [1, 5, 3], "REB": [5, 4, 2]}),
            {"PR": "PTS+REB"},
            pd.DataFrame({"PTS": [1, 5, 3], "REB": [5, 4, 2], "PR": [6, 9, 5]}),
        ),
        (
            pd.DataFrame({"PTS": [1, 5, 3], "REB": [5, 4, 2]}),
            {"PR": lambda df: df["PTS"] + df["REB"]},
            pd.DataFrame({"PTS": [1, 5, 3], "REB": [5, 4, 2], "PR": [6, 9, 5]}),
        ),
    ),
)
def test_augment_dataframe(
    dataframe: pd.DataFrame,
    augmentations: Mapping[str, str | Callable[[pd.DataFrame], pd.Series]],
    expected: pd.DataFrame,
):
    result = augment_dataframe(dataframe, augmentations)

    assert result.equals(expected)


@pytest.mark.parametrize(
    "dataframe, augmentations",
    (
        (pd.DataFrame(), {"key": 10}),
        (pd.DataFrame(), 10),
        (pd.DataFrame(), None),
        ({"PTS": 10, "REB": 5}, {"PR": lambda df: df["PTS"] + df["REB"]}),
    ),
)
def test_augment_dataframe_illegal_arguments(dataframe, augmentations):
    with pytest.raises(TypeError) as error:
        augment_dataframe(dataframe, augmentations)
