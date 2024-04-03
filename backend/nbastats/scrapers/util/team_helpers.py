from typing import Optional

import numpy as np
from exceptions import DBNotFoundException
from nbastats.sql_app.register import Teams
from pydantic import UUID4


def get_team_id_by_abbr(team_abbr: str) -> UUID4 | float:
    if type(team_abbr) != str and np.isnan(team_abbr):
        return np.nan

    team_abbr = team_abbr.split(",")[0]

    team = Teams.get_team_by_abbr(team_abbr=team_abbr)

    if not team:
        # raise DBNotFoundException(f"Could not find team with abbreviation {team_abbr}.")
        return np.nan

    return team.id
