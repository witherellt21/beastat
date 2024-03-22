from base.sql_app.register import BaseTable
from nbastats.sql_app.database import DB
from nbastats.sql_app.models import DefenseRanking
from nbastats.sql_app.serializers import DefenseRankingSerializer


class DefenseRankingTable(BaseTable):
    MODEL_CLASS = DefenseRanking
    SERIALIZER_CLASS = DefenseRankingSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = DefenseRankingSerializer
    PKS = ["team", "stat"]


# DefenseRankings = DefenseRankingTable(DB)
