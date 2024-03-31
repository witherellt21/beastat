import logging
import uuid

import pandas as pd
from nbastats.sql_app.register import PlayerProps
from nbastats.sql_app.util.db_helpers import get_player_id

from .utils import get_game_id, get_player_props, set_statuses

logger = logging.getLogger("main")


IDENTIFICATION_FUNCTION = lambda tables: pd.concat(tables)
SQL_TABLE = PlayerProps
NAME = "GamesTable"

CONFIG = {
    "rename_columns": {
        "PLAYER": "name",
    },
    "rename_values": {
        "stat": {
            "points": "PTS",
            "assists": "AST",
            "threes": "THP",
            "rebounds": "TRB",
            "pts-+-reb-+-ast": "PRA",
            "pts-+-reb": "PR",
            "pts-+-ast": "PA",
            "ast-+-reb": "RA",
        }
    },
    "transformations": {
        ("name", "player_id"): lambda name: get_player_id(player_name=name),
        ("name", "id"): lambda x: uuid.uuid4(),
        ("player_id", "game_id"): lambda player_id: get_game_id(player_id=player_id),
    },
    "data_transformations": [get_player_props, set_statuses],
    "query_save_columns": {"stat": "stat_subcategory"},
    "required_columns": ["player_id"],
}
