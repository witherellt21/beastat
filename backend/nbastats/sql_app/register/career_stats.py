from base.sql_app.register import BaseTable
from nbastats.sql_app.database import DB
from nbastats.sql_app.models.career_stats import CareerStats
from nbastats.sql_app.models.player import Player
from nbastats.sql_app.serializers.career_stats import (
    CareerStatsReadSerializer,
    CareerStatsSerializer,
    CareerStatsTableEntrySerializer,
)


class CareerStatsTable(BaseTable):
    MODEL_CLASS = CareerStats
    SERIALIZER_CLASS = CareerStatsSerializer
    READ_SERIALIZER_CLASS = CareerStatsReadSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = CareerStatsTableEntrySerializer
    PKS = ["player_id", "Season"]

    DEPENDENCIES = [Player]


CareerStatss = CareerStatsTable(DB)
