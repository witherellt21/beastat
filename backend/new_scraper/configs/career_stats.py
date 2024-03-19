import uuid

import numpy as np
from exceptions import DBNotFoundException
from new_scraper.base import BaseHTMLDatasetConfig
from new_scraper.util.string_helpers import convert_season_to_year
from sql_app.register import CareerStatss, Teams


def get_team_id_by_abbr(team_abbr: str):
    if type(team_abbr) != str and np.isnan(team_abbr):
        return np.nan

    team = Teams.get_team_by_abbr(team_abbr=team_abbr)

    if not team:
        raise DBNotFoundException(f"Could not find team with abbreviation {team_abbr}.")

    return team.id


class CareerStatsTableConfig(BaseHTMLDatasetConfig):
    """
    Here we will include the cleaning function stuff as class attributes
    """

    STAT_AUGMENTATIONS = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
    }

    TRANSFORMATIONS = {
        "Season": lambda season: convert_season_to_year(season=season),
        ("PTS", "id"): lambda x: uuid.uuid4(),
        ("Tm", "Tm_id"): get_team_id_by_abbr,
    }

    _exception_msgs = {
        "load_data": f"Error reading saved player overview from csv.",
        "download_data": f"Error fetching (http) player overview from html.",
    }

    RENAME_COLUMNS = {
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "2P": "TWP",
        "2PA": "TWPA",
        "2P%": "TWP_perc",
        "eFG%": "eFG_perc",
        "FT%": "FT_perc",
    }
    QUERY_SAVE_COLUMNS = {"player_id": "player_id"}
    REQUIRED_FIELDS = ["Season", "G"]

    # TABLE = Players
    # LOG_LEVEL = logging.WARNING

    def __init__(self):
        super().__init__(
            identification_function=lambda dataset: "Season" in dataset.columns,
            sql_table=CareerStatss,
        )

    @property
    def base_download_url(self):
        return "http://www.basketball-reference.com/players/{player_last_initial}/{player_id}.html"
