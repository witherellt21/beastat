from decimal import Decimal
from typing import Callable

import pandas as pd

MATHEMATICAL_OPERATORS = ("+", "-")
OPERABLE_TYPES = (None, int, float, Decimal)


OPERATOR_FUNCTION_MAP: dict[str, Callable[[int | float, int | float], int | float]] = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
}


def get_expression_stack(formula: str) -> list:
    """
    Convert the string to an expressions stack. Only supports addition and subtraction.
    """

    if type(formula) != str:
        raise TypeError("Argument 'formula' must be a string.")

    current_var = ""
    expression_stack = []

    for char in formula:
        if char in OPERATOR_FUNCTION_MAP:
            if not current_var:
                raise ValueError(
                    "Operator reached before variable. Make sure your equation syntax is correct."
                )

            expression_stack.extend([OPERATOR_FUNCTION_MAP[char], current_var])
            current_var = ""

        else:
            current_var += char

    if current_var:
        expression_stack.append(current_var)
    else:
        raise ValueError(
            "Operator did not receive a second operand. Make sure your equation syntax is correct."
        )

    return expression_stack


def evaluate_expression(
    dataframe: pd.DataFrame,
    expression_stack: list[Callable[[pd.Series, pd.Series], pd.Series] | str],
) -> pd.Series:
    """
    Perform an expression containing pandas dataframe columns and constants.
    Provide a dataframe as well as an expression stack containing operators and operands
    in binary stack notation:
        [operator, operand1, operand2]

    Operators must be callable functions that take 2 series, and return the result of an operation
    on the 2 series.
    """
    if not expression_stack:
        raise ValueError("Ran out of operators.")

    operator = expression_stack.pop(0)

    if callable(operator):
        return operator(
            evaluate_expression(dataframe, expression_stack[:1]),
            evaluate_expression(dataframe, expression_stack[1:]),
        )

    else:
        try:
            constant = eval(operator)

            if type(constant) in OPERABLE_TYPES:
                return pd.Series([constant] * len(dataframe))

            else:
                raise NameError()

        except NameError as e:

            if expression_stack:
                raise ValueError(
                    "Leftover operands. Check your operation stack to ensure there are n operators and n+1 operands."
                )

            if operator not in dataframe.columns:
                raise KeyError(
                    f"Operand {operator} not present in dataframe columns. Options are: {dataframe.columns}."
                )

            return dataframe[operator]
