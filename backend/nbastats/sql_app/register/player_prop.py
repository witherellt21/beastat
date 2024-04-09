from core.sql_app.register import BaseTable
from nbastats.sql_app.models import PropLine
from nbastats.sql_app.serializers import PlayerPropReadSerializer, PlayerPropSerializer


class PlayerPropTable(BaseTable):
    MODEL_CLASS = PropLine
    SERIALIZER_CLASS = PlayerPropSerializer
    READ_SERIALIZER_CLASS = PlayerPropReadSerializer
    PKS = ["player_id", "stat"]
