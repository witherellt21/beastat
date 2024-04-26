from typing import Any, Callable, Mapping

import pandas as pd

from .augmentations import evaluate_expression, get_expression_stack

MATHEMATICAL_OPERATORS = ["+", "-"]


def reorder_columns(
    *, dataframe: pd.DataFrame, column_order: list[str]
) -> pd.DataFrame:
    columns = list(dataframe)
    for column in reversed(column_order):
        try:
            columns.insert(0, columns.pop(columns.index(column)))
        except ValueError:
            continue

    return dataframe.loc[:, columns]


def filter_dataframe(
    *, dataframe: pd.DataFrame, filters: "list[Callable]"
) -> pd.DataFrame:
    for _filter in filters:
        dataframe = dataframe[dataframe.apply(_filter, axis=1)].reset_index(drop=True)
    return dataframe


def augment_dataframe(
    *,
    dataframe: pd.DataFrame,
    augmentations: Mapping[str, str | Callable[[pd.DataFrame], pd.Series]]
):
    """
    Augment the dataset using the passed dictionary of key: expression pairings and evaluating
    - Use Semantic Analysis to parse the a string string expression into an evaluation.
    - Assigns the resulting evaluation to the provided key in the dataset
    """

    for key, augmentation in augmentations.items():
        if isinstance(augmentation, str):
            operation_stack = get_expression_stack(augmentation)

            dataframe[key] = evaluate_expression(dataframe, operation_stack)

        elif isinstance(augmentation, Callable):
            dataframe[key] = augmentation(dataframe)

    return dataframe


def filter_with_bounds(
    dataset: pd.DataFrame, column: str, bounds: tuple[Any, Any]
) -> pd.DataFrame:
    _min, _max = bounds
    if _min is not None and _max is not None:
        if _min < _max:
            dataset = dataset[dataset[column].between(_min, _max)]
        elif _min > _max:
            dataset = dataset[~dataset[column].between(_min, _max)]
        else:
            dataset = dataset[dataset[column] == _min]
    elif _min is not None:
        dataset = dataset[dataset[column] >= _min]
    elif _max is not None:
        dataset = dataset[dataset[column] <= _max]

    return dataset
