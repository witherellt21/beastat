from base.sql_app.register import BaseTable
from nbastats.sql_app.models import DefenseRanking
from nbastats.sql_app.serializers import (
    DefenseRankingSerializer,
    DefenseRankingTableEntrySerializer,
)


class DefenseRankingTable(BaseTable):
    MODEL_CLASS = DefenseRanking
    SERIALIZER_CLASS = DefenseRankingSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = DefenseRankingTableEntrySerializer
    PKS = ["team", "stat"]


# DefenseRankings = DefenseRankingTable(DB)
