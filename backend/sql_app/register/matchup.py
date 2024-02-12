from sql_app.models.matchup import Matchup
from sql_app.serializers.matchup import MatchupSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable


class MatchupTable(BaseTable):
    MODEL_CLASS = Matchup
    SERIALIZER_CLASS = MatchupSerializer
    PKS = ["id"]


Matchups = MatchupTable(DB)
