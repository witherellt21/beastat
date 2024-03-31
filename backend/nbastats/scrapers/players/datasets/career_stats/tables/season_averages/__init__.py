import uuid

import numpy as np
from nbastats.global_implementations import constants
from nbastats.global_implementations.string_helpers import convert_season_to_year
from nbastats.scrapers.players.datasets.career_stats.tables.season_averages.util import (
    get_cached_player_season_averages_data,
    has_season_column,
)
from nbastats.scrapers.util.team_helpers import get_team_id_by_abbr
from nbastats.sql_app.register import SeasonAveragess

NAME = "SeasonAverages"

SQL_TABLE = SeasonAveragess

IDENTIFICATION_FUNCTION = has_season_column

CONFIG = {
    "stat_augmentations": {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
    },
    "rename_columns": {
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "2P": "TWP",
        "2PA": "TWPA",
        "2P%": "TWP_perc",
        "eFG%": "eFG_perc",
        "FT%": "FT_perc",
    },
    "rename_values": {
        "Tm": {"TOT": np.nan},
        "TWP_perc": {"": np.nan},
        "THP_perc": {"": np.nan},
        "FT_perc": {"": np.nan},
        "FG_perc": {"": np.nan},
        "eFG_perc": {"": np.nan},
    },
    "transformations": {
        "Season": lambda season: convert_season_to_year(season=season),
        ("PTS", "id"): lambda x: uuid.uuid4(),
        ("Tm", "Tm_id"): get_team_id_by_abbr,
    },
    "nan_values": constants.NAN_VALUES,
    "data_transformations": [],
    "query_save_columns": {"player_id": "player_id"},
    "required_fields": ["Season", "G", "Tm"],
    "cached_query_generator": get_cached_player_season_averages_data,
}
