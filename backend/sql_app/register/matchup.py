from sql_app.database import DB
from sql_app.models.matchup import Matchup
from sql_app.register.base import BaseTable
from sql_app.serializers.matchup import MatchupReadSerializer, MatchupSerializer


class MatchupTable(BaseTable):
    MODEL_CLASS = Matchup
    SERIALIZER_CLASS = MatchupSerializer
    READ_SERIALIZER_CLASS = MatchupReadSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = MatchupSerializer
    PKS = ["game_id", "position"]


Matchups = MatchupTable(DB)
