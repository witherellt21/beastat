from base.sql_app.register import BaseTable
from nbastats.sql_app.models import CareerStats
from nbastats.sql_app.register.player import PlayerTable
from nbastats.sql_app.register.team import TeamTable
from nbastats.sql_app.serializers import (
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

    DEPENDENCIES = [PlayerTable, TeamTable]


# CareerStatss = CareerStatsTable(DB)
