from base.sql_app.register import BaseTable
from nbastats.sql_app.models import Matchup
from nbastats.sql_app.serializers import MatchupReadSerializer, MatchupSerializer


class MatchupTable(BaseTable):
    MODEL_CLASS = Matchup
    SERIALIZER_CLASS = MatchupSerializer
    READ_SERIALIZER_CLASS = MatchupReadSerializer
    PKS = ["game_id", "position"]
