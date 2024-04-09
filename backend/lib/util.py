import os
from functools import reduce
from typing import Any, Type, Union

import numpy as np


def construct_file_path(path: str) -> None:
    """
    Construct recursive file path.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def is_dir_module(*, module_path: str) -> bool:
    """
    Returns whether or not the path is a python directory module.
    """
    return os.path.isdir(module_path) and "__init__.py" in os.listdir(module_path)


def is_file_module(*, module_name: str) -> bool:
    """
    Returns whether or not the path is a python file module.
    """
    return module_name.split(".")[-1] == "py"


def camel_to_snake_case(str):
    """
    Conver camel case string to snake case.
    """
    res = [str[0].lower()]
    for c in str[1:]:
        if c in ("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
            res.append("_")
            res.append(c.lower())

        else:
            res.append(c)

    return "".join(res)


def sum_nullables(*args, type: Type[Union[int, float]] = float):
    """
    Sum a number of arguments by converting them to the specified type.

    Treat 0 as np.nan.
    """
    total: type = 0
    valid = False
    for arg in args:
        if arg != np.nan:
            valid = True
            total += type(arg)

    return total if valid else np.nan


def combine_lists_of_dicts(*lists):
    """
    Combine the lists of dictionaries.
    """
    combined_list = [
        reduce(lambda d1, d2: {**d1, **d2}, dicts) for dicts in zip(*lists)
    ]
    return combined_list


def list_difference(*, source: list[Any], to_remove: list[Any]):
    """
    Remove items from list.
    """
    for item in to_remove:
        if item in source:
            source.remove(item)

    return source
