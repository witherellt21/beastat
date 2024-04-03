from base.sql_app.register import BaseTable
from nbastats.sql_app.models import PropLine
from nbastats.sql_app.serializers import PlayerPropSerializer, ReadPlayerPropSerializer


class PlayerPropTable(BaseTable):
    MODEL_CLASS = PropLine
    SERIALIZER_CLASS = PlayerPropSerializer
    READ_SERIALIZER_CLASS = ReadPlayerPropSerializer
    PKS = ["player_id", "stat"]
