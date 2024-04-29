from typing import Any, Callable, Mapping

import pandas as pd

from .augmentations import evaluate_expression, get_expression_stack

MATHEMATICAL_OPERATORS = ["+", "-"]


def filter_dataframe(dataframe: pd.DataFrame, filters: list[Callable]) -> pd.DataFrame:
    """
    Filter a dataframe by a set of callable boolean filters.
    Returns the original dataset filtered by the provided filters.
    """
    for _filter in filters:
        if _filter.__code__.co_argcount != 1:
            raise ValueError("Filters must contain exactly one argument.")

        proxy = dataframe.apply(_filter, axis=1)

        if proxy.dtype != bool:
            raise ValueError("Filters must return boolean values.")

        dataframe = dataframe[dataframe.apply(_filter, axis=1)].reset_index(drop=True)
    return dataframe


def augment_dataframe(
    dataframe: pd.DataFrame,
    augmentations: Mapping[str, str | Callable[[pd.DataFrame], pd.Series]],
):
    """
    Augment the dataset using the passed dictionary of key: expression pairings and evaluating
    - Use Semantic Analysis to parse the a string string expression into an evaluation.
    - Assigns the resulting evaluation to the provided key in the dataset
    """
    if not isinstance(augmentations, Mapping):
        raise TypeError(
            "Augmentations must be a mapping with a dataframe column to callable function pairing."
        )

    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("'dataframe' must be of type pandas.Dataframe().")

    for key, augmentation in augmentations.items():
        if isinstance(augmentation, str):
            operation_stack = get_expression_stack(augmentation)

            dataframe[key] = evaluate_expression(dataframe, operation_stack)

        elif isinstance(augmentation, Callable):
            dataframe[key] = augmentation(dataframe)

        else:
            raise TypeError(f"Invalid augmentation function: {augmentation}.")

    return dataframe


def filter_with_bounds(
    dataframe: pd.DataFrame, column: str, bounds: tuple[Any, Any]
) -> pd.DataFrame:
    """
    Filter a dataframe column between 2 bounds.
    """
    _min, _max = bounds
    if _min is not None and _max is not None:
        if _min < _max:
            dataframe = dataframe[dataframe[column].between(_min, _max)]
        elif _min > _max:
            dataframe = dataframe[~dataframe[column].between(_max, _min)]
        else:
            dataframe = dataframe[dataframe[column] == _min]
    elif _min is not None:
        dataframe = dataframe[dataframe[column] >= _min]
    elif _max is not None:
        dataframe = dataframe[dataframe[column] <= _max]

    return dataframe
