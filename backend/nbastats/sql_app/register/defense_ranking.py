from core.sql_app.register import BaseTable

from .models import DefenseRanking
from .serializers import DefenseRankingSerializer


class DefenseRankingTable(BaseTable):
    MODEL_CLASS = DefenseRanking
    SERIALIZER_CLASS = DefenseRankingSerializer
    PKS = ["team", "stat"]
