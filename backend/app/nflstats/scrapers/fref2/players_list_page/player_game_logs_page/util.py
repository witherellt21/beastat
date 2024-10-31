from typing import Literal


def convert_age_to_age_years(age: str) -> int:
    return int(age.split(".", 1)[0])


def convert_age_to_age_days(age: str) -> int:
    return int(age.split(".", 1)[1])


def convert_home_away(val: str) -> bool:
    if val not in ["", "@"]:
        raise ValueError(f"Result does not contain either '' or '@' data. Got {val}")

    return not val == "@"


def convert_result_to_win_loss_tie(result: str) -> str:
    win_loss_tie = result.split(" ", 1)[0]

    if win_loss_tie not in ["W", "L", "T"]:
        raise ValueError(
            f"Result does not contain either 'W', 'L', or 'T' data. Got {result}"
        )

    return win_loss_tie


def convert_result_to_team_pts(result: str) -> int:
    score = result.split(" ", 1)[1]

    return int(score.split("-")[0])


def convert_result_to_opp_pts(result: str) -> int:
    score = result.split(" ", 1)[1]

    return int(score.split("-")[1])


def convert_GS_to_start_bool(gs: Literal["", "*"]) -> bool:
    if gs not in ["", "*"]:
        raise ValueError(f"GS does not contain either '' or '*' data. Got: {gs}")

    return gs == "*"
