from sql_app.models.player_prop import Player
from sql_app.models.player_prop import PropLine
from sql_app.serializers.player_prop import PlayerPropSerializer
from sql_app.serializers.player_prop import PropLineSerializer
from sql_app.serializers.player_prop import ReadPlayerPropSerializer
from sql_app.serializers.player_prop import ReadPropLineSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable


class PlayerPropTable(BaseTable):
    MODEL_CLASS = Player
    SERIALIZER_CLASS = PlayerPropSerializer
    READ_SERIALIZER_CLASS = ReadPlayerPropSerializer
    PKS = ["player_id", "stat"]


class PropLineTable(BaseTable):
    MODEL_CLASS = PropLine
    SERIALIZER_CLASS = PropLineSerializer
    READ_SERIALIZER_CLASS = ReadPropLineSerializer
    PKS = ["player_id", "stat"]


PlayerProps = PlayerPropTable(DB)
PropLines = PropLineTable(DB)
