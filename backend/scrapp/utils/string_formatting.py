from typing import Literal


def generate_bulleted_list(
    input: dict | list, bullet_type: Literal["-", "num"] = "-", indentation: int = 3
) -> str:
    """
    Format a dictionary's attributes out in a list-like display.
    """
    if bullet_type == "num":
        bullets = [f"{i}." for i in range(len(input))]
    else:
        bullets = [bullet_type] * len(input)

    indent = " " * indentation

    idx, res_str = 0, ""
    for inp in input:
        if type(input) == dict:
            res_str += f"\n{indent}{bullets[idx]} {inp} = {input[inp]}"

        elif type(input) == list:
            res_str += f"\n{indent}{bullets[idx]} {inp}"
        idx += 1

    return res_str


def generate_inline_list(input: dict) -> str:
    """
    Format a dictionary's attributes out in a list-like display.
    """
    return ", ".join(" = ".join([key, value]) for key, value in input.items())
