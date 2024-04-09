from nbastats.lib import constants
from nbastats.scrapers.bref.datasets.career_stats.tables.season_averages.util import (
    SeasonAveragesTableEntrySerializer,
    get_cached_player_season_averages_data,
    has_season_column,
)
from nbastats.sql_app.register import SeasonAveragess

NAME = "SeasonAverages"

SQL_TABLE = SeasonAveragess

IDENTIFICATION_FUNCTION = has_season_column

TABLE_SERIALIZER = SeasonAveragesTableEntrySerializer()

CONFIG = {
    "nan_values": constants.NAN_VALUES,
    "cached_query_generator": get_cached_player_season_averages_data,
}
