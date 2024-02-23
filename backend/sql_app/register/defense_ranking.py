from sql_app.models.defense_ranking import DefenseRanking
from sql_app.serializers.defense_ranking import DefenseRankingSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable


class DefenseRankingTable(BaseTable):
    MODEL_CLASS = DefenseRanking
    SERIALIZER_CLASS = DefenseRankingSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = DefenseRankingSerializer
    PKS = ["team", "stat"]


DefenseRankings = DefenseRankingTable(DB)
