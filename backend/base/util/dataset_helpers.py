from typing import Any, Callable, Mapping, Optional

import pandas as pd

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

    def evaluate(operation_list: list) -> pd.Series:
        """A recursive function for evaluating a semantic expression in binary tree form."""
        if not operation_list:
            raise Exception("Ran out of operators.")

        operator = operation_list.pop(0)

        if callable(operator):
            return operator(evaluate(operation_list[:1]), evaluate(operation_list[1:]))
        else:
            return dataframe[operator]

    for key, augmentation in augmentations.items():
        if isinstance(augmentation, str):
            operation_list = get_operation(augmentation)
            dataframe[key] = evaluate(operation_list)
        elif isinstance(augmentation, Callable):
            dataframe[key] = augmentation(dataframe)

    return dataframe


def get_operation(formula: str):
    """Convert the string to an operation. Only supports addition and subtraction."""

    def get_operator_func(operator: str):
        if operator == "+":
            return lambda x, y: x + y
        elif operator == "-":
            return lambda x, y: x - y

    current_var = ""
    operation_list = []
    for char in formula:
        if char in MATHEMATICAL_OPERATORS:
            operation_list.append(get_operator_func(char))
            operation_list.append(current_var)
            current_var = ""
        else:
            current_var += char

    if current_var:
        operation_list.append(current_var)

    return operation_list


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


if __name__ == "__main__":
    operation = get_operation("PTS+AST+TRB")
    print(operation)

    df = pd.DataFrame({"PTS": [1, 2, 3, 4], "TRB": [2, 3, 4, 5], "AST": [3, 4, 5, 6]})
    augmentations = {"PR": "PTS+TRB", "PA": "PTS+AST", "PRA": "PTS+AST+TRB"}
    df = augment_dataframe(dataframe=df, augmentations=augmentations)
    print(df)
