import pandas as pd

MATHEMATICAL_OPERATORS = ["+", "-"]


def get_operation_stack(formula: str):
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


def evaluate(dataframe: pd.DataFrame, operation_list: list) -> pd.Series:
    """A recursive function for evaluating a semantic expression in binary tree form."""
    if not operation_list:
        raise Exception("Ran out of operators.")

    operator = operation_list.pop(0)

    if callable(operator):
        return operator(
            evaluate(dataframe, operation_list[:1]),
            evaluate(dataframe, operation_list[1:]),
        )
    else:
        return dataframe[operator]
