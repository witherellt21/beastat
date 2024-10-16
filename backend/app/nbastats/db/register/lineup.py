from core.db.tables import BaseTable

from .models import Lineup
from .serializers import LineupReadSerializer, LineupSerializer


class LineupTable(BaseTable):
    MODEL_CLASS = Lineup
    SERIALIZER_CLASS = LineupSerializer
    READ_SERIALIZER_CLASS = LineupReadSerializer
    PKS = ["game_id", "team_id"]
