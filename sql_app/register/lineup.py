from sql_app.models.lineup import Lineup
from sql_app.serializers.lineup import LineupSerialzer

from sql_app.database import DB
from sql_app.register.base import BaseTable

class LineupTable(BaseTable):
    MODEL_CLASS = Lineup
    SERIALIZER_CLASS = LineupSerialzer
    PKS = ["game_id", "team"]

Lineups = LineupTable(DB)