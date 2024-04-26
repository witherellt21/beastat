import numpy as np
import pandas as pd
import pytest
from lib.augmentations.operations import evaluate, get_operation_stack


@pytest.mark.parametrize(
    "formula, expected_length",
    (
        ("PTS+REB", 3),
        ("3+2", 3),
        ("2-REB", 3),
        ("2-REB+REB", 5),
        ("word + name", 3),
        ("word*name", 1),
        ("word/name", 1),
        ("word^2", 1),
    ),
)
def test_get_operation_stack(formula: str, expected_length: int):
    res = get_operation_stack(formula)

    assert type(res) == list
    assert len(res) == expected_length

    for i in range(0, expected_length - 1, 2):
        assert callable(res[i])

    for i in range(1, expected_length, 2):
        assert type(res[i]) == str

    assert type(res[-1]) == str


@pytest.mark.parametrize(
    "formula",
    (3, 3.5, None, dict(), list(), set(), True),
)
def test_get_operation_stack_illegal_argument_type(formula: str):
    with pytest.raises(TypeError) as error:
        res = get_operation_stack(formula)


@pytest.mark.parametrize(
    "formula",
    (
        "+REB",
        "3++2",
        "--REB",
        "2-+REB",
        "word+",
    ),
)
def test_get_operation_stack_illegal_argument_format(formula: str):
    with pytest.raises(ValueError) as error:
        res = get_operation_stack(formula)


@pytest.mark.parametrize(
    "dataframe, operation_list, expected",
    (
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [2, 1]}),
            get_operation_stack("PTS+REB"),
            pd.Series([5, 6]),
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [2, 1]}),
            get_operation_stack("PTS+REB+2"),
            pd.Series([7, 8]),
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [2, 1]}),
            get_operation_stack("PTS-REB"),
            pd.Series([1, 4]),
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [0.5, 1]}),
            get_operation_stack("PTS-REB"),
            pd.Series([2.5, 4]),
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [None, 1]}),
            get_operation_stack("PTS-REB"),
            pd.Series([np.nan, 4]),
        ),
    ),
)
def test_evaluate(dataframe: pd.DataFrame, operation_list: list, expected: pd.Series):
    res = evaluate(dataframe, operation_list)

    assert res.equals(expected)


@pytest.mark.parametrize(
    "dataframe, operation_list",
    (
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [2, 1]}),
            [lambda x, y: x + y, "PTS"],
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [2, 1]}),
            [],
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [2, 1]}),
            ["PTS", "REB"],
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [2, 1]}),
            ["PTS", lambda x, y: x + y],
        ),
    ),
)
def test_evaluate_value_error(dataframe: pd.DataFrame, operation_list: list):
    with pytest.raises(ValueError) as error:
        res = evaluate(dataframe, operation_list)


@pytest.mark.parametrize(
    "dataframe, operation_list",
    (
        (
            pd.DataFrame({"PTS": [3, 5]}),
            [lambda x, y: x + y, "PTS", "REB"],
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [dict(), 1]}),
            [lambda x, y: x + y, "PTS", "dict"],
        ),
    ),
)
def test_evaluate_key_error(dataframe: pd.DataFrame, operation_list: list):
    with pytest.raises(KeyError) as error:
        res = evaluate(dataframe, operation_list)


@pytest.mark.parametrize(
    "dataframe, operation_list",
    (
        (
            pd.DataFrame({"PTS": [3, 5], "REB": ["String", 1]}),
            [lambda x, y: x + y, "PTS", "REB"],
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [list(), 1]}),
            [lambda x, y: x + y, "PTS", "REB"],
        ),
        (
            pd.DataFrame({"PTS": [3, 5], "REB": [dict(), 1]}),
            [lambda x, y: x + y, "PTS", "REB"],
        ),
    ),
)
def test_evaluate_type_error(dataframe: pd.DataFrame, operation_list: list):
    with pytest.raises(TypeError) as error:
        res = evaluate(dataframe, operation_list)
        print(error)
