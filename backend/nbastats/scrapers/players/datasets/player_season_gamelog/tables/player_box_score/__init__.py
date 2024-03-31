import uuid

import numpy as np
from nbastats.global_implementations import constants
from nbastats.scrapers.players.datasets.player_season_gamelog.tables.player_box_score.util import *
from nbastats.sql_app.register import PlayerBoxScores

NAME = "PlayerBoxScore"

SQL_TABLE = PlayerBoxScores

IDENTIFICATION_FUNCTION = has_30_columns

CONFIG = {
    "filters": [],
    "datetime_columns": {"Date": "%Y-%m-%d"},
    "rename_columns": {
        "FT%": "FT_perc",
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "+/-": "plus_minus",
    },
    "rename_values": {
        "Rk": {"Rk": np.nan},
        "G": {"": np.nan},
        "TWP_perc": {"": np.nan},
        "THP_perc": {"": np.nan},
        "FT_perc": {"": np.nan},
        "FG_perc": {"": np.nan},
    },
    "transformations": {
        "MP": lambda x: convert_minutes_to_float(x),
        ("PTS", "id"): lambda x: uuid.uuid4(),
        ("Unnamed: 5", "home"): lambda cell: cell != "@",
    },
    "data_transformations": [get_result_and_margin],
    "stat_augmentations": {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
        "days_rest": get_days_rest,
        "game_id": get_game_ids,
    },
    "nan_values": constants.NAN_VALUES,
    "query_save_columns": {"player_id": "player_id"},
    "required_fields": ["Rk"],
    "href_save_map": {},
    "cached_query_generator": get_cached_gamelog_query_data,
    # "column_ordering": ["player_id"]
}
