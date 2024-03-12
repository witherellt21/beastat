from pydantic import UUID4
from sql_app.register import Teams
from exceptions import DBNotFoundException


def get_team_id_by_abbr(team_abbr: str) -> UUID4:
    team_abbr = team_abbr.split(",")[0]

    team = Teams.get_team_by_abbr(team_abbr=team_abbr)

    if not team:
        raise DBNotFoundException(f"Could not find team with abbreviation {team_abbr}.")

    return team.id
