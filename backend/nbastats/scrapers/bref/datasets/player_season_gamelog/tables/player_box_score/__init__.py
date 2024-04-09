from nbastats import constants
from nbastats.scrapers.bref.datasets.player_season_gamelog.tables.player_box_score.util import (
    PlayerBoxScoreTableConfig,
    get_cached_gamelog_query_data,
    has_30_columns,
)
from nbastats.sql_app.register import PlayerBoxScores

NAME = "PlayerBoxScore"

SQL_TABLE = PlayerBoxScores

IDENTIFICATION_FUNCTION = has_30_columns

TABLE_SERIALIZER = PlayerBoxScoreTableConfig()

CONFIG = {
    "nan_values": constants.NAN_VALUES,
    "cached_query_generator": get_cached_gamelog_query_data,
}
