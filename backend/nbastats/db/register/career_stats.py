from core.db.tables import BaseTable

from .models import CareerStats
from .player import PlayerTable
from .serializers import CareerStatsReadSerializer, CareerStatsSerializer
from .team import TeamTable


class CareerStatsTable(BaseTable):
    MODEL_CLASS = CareerStats
    SERIALIZER_CLASS = CareerStatsSerializer
    READ_SERIALIZER_CLASS = CareerStatsReadSerializer
    PKS = ["player_id", "Season"]

    DEPENDENCIES = [PlayerTable, TeamTable]
