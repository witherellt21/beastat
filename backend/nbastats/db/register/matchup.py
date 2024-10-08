from core.db.tables import BaseTable

from .models import Matchup
from .serializers import MatchupReadSerializer, MatchupSerializer


class MatchupTable(BaseTable):
    MODEL_CLASS = Matchup
    SERIALIZER_CLASS = MatchupSerializer
    READ_SERIALIZER_CLASS = MatchupReadSerializer
    PKS = ["game_id", "position"]
