from calendar import day_abbr
from decimal import Decimal
from typing import Callable, TypeVar

import pandas as pd

MATHEMATICAL_OPERATORS = ("+", "-")
OPERABLE_TYPES = (None, int, float, Decimal)


OPERATOR_FUNCTION_MAP: dict[str, Callable[[int | float, int | float], int | float]] = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
}


def get_operation_stack(formula: str) -> list:
    """Convert the string to an operation. Only supports addition and subtraction."""

    if type(formula) != str:
        raise TypeError("Argument 'formula' must be a string.")

    current_var = ""
    operation_list = []

    for char in formula:
        if char in OPERATOR_FUNCTION_MAP:
            operation_list.append(OPERATOR_FUNCTION_MAP[char])
            if not current_var:
                raise ValueError(
                    "Operator reached before variable. Make sure your equation syntax is correct."
                )

            operation_list.append(current_var)
            current_var = ""
        else:
            current_var += char

    if current_var:
        operation_list.append(current_var)
    else:
        raise ValueError(
            "Operator did not receive a second operand. Make sure your equation syntax is correct."
        )

    return operation_list


def evaluate(
    dataframe: pd.DataFrame,
    operation_list: list[Callable[[pd.Series, pd.Series], pd.Series] | str],
) -> pd.Series:
    """A recursive function for evaluating a semantic expression in binary tree form."""
    if not operation_list:
        raise ValueError("Ran out of operators.")

    operator = operation_list.pop(0)

    if callable(operator):
        return operator(
            evaluate(dataframe, operation_list[:1]),
            evaluate(dataframe, operation_list[1:]),
        )

    else:
        try:
            constant = eval(operator)

            if type(constant) in OPERABLE_TYPES:
                return pd.Series([constant] * len(dataframe))

            else:
                raise NameError()

        except NameError as e:

            if operation_list:
                raise ValueError(
                    "Leftover operands. Check your operation stack to ensure there are n operators and n+1 operands."
                )

            if operator not in dataframe.columns:
                raise KeyError(
                    f"Operand {operator} not present in dataframe columns. Options are: {dataframe.columns}."
                )

            return dataframe[operator]
