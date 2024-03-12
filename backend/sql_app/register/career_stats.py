from sql_app.models.career_stats import CareerStats
from sql_app.models.player import Player
from sql_app.serializers.career_stats import (
    CareerStatsSerializer,
    CareerStatsReadSerializer,
    CareerStatsTableEntrySerializer,
)

from sql_app.database import DB
from sql_app.register.base import BaseTable


class CareerStatsTable(BaseTable):
    MODEL_CLASS = CareerStats
    SERIALIZER_CLASS = CareerStatsSerializer
    READ_SERIALIZER_CLASS = CareerStatsReadSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = CareerStatsTableEntrySerializer
    PKS = ["player_id", "Season"]

    DEPENDENCIES = [Player]


CareerStatss = CareerStatsTable(DB)
