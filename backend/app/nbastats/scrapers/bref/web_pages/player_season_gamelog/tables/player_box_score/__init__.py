from nbastats import constants
from nbastats.db.register import PlayerBoxScores
from nbastats.scrapers.bref.web_pages.player_season_gamelog.tables.player_box_score.util import (
    PlayerBoxScoreTableConfig,
    get_cached_gamelog_query_data,
    has_30_columns,
)

NAME = "PlayerBoxScore"

SQL_TABLE = PlayerBoxScores

IDENTIFICATION_FUNCTION = has_30_columns

TABLE_SERIALIZER = PlayerBoxScoreTableConfig()

CONFIG = {
    "nan_values": constants.NAN_VALUES,
    "cached_query_generator": get_cached_gamelog_query_data,
}
