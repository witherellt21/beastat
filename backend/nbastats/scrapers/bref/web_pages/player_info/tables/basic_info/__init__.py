from nbastats.db.register import BasicInfo
from nbastats.scrapers.bref.web_pages.player_info.tables.basic_info.util import (
    PlayerInfoTableEntrySerializer,
    get_cached_player_info_data,
    has_player_column,
)

NAME = "BasicInfo"

SQL_TABLE = BasicInfo

IDENTIFICATION_FUNCTION = has_player_column

TABLE_SERIALIZER = PlayerInfoTableEntrySerializer()

CONFIG = {"cached_query_generator": get_cached_player_info_data}
