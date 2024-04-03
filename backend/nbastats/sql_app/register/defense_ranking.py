from core.sql_app.register import BaseTable
from nbastats.sql_app.models import DefenseRanking
from nbastats.sql_app.serializers import DefenseRankingSerializer


class DefenseRankingTable(BaseTable):
    MODEL_CLASS = DefenseRanking
    SERIALIZER_CLASS = DefenseRankingSerializer
    PKS = ["team", "stat"]
