from base.sql_app.register import BaseTable
from nbastats.sql_app.models import Lineup
from nbastats.sql_app.serializers import LineupReadSerializer, LineupSerializer


class LineupTable(BaseTable):
    MODEL_CLASS = Lineup
    SERIALIZER_CLASS = LineupSerializer
    READ_SERIALIZER_CLASS = LineupReadSerializer
    PKS = ["game_id", "team_id"]
