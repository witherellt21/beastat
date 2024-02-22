from sql_app.models.career_stats import CareerStats
from sql_app.serializers.career_stats import CareerStatsSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable


class CareerStatsTable(BaseTable):
    MODEL_CLASS = CareerStats
    SERIALIZER_CLASS = CareerStatsSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = CareerStatsSerializer
    PKS = ["player_id", "Season"]


CareerStatss = CareerStatsTable(DB)
