from sql_app.models.player_prop import PlayerProp
from sql_app.serializers.player_prop import PlayerPropSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable


class PlayerPropTable(BaseTable):
    MODEL_CLASS = PlayerProp
    SERIALIZER_CLASS = PlayerPropSerializer
    PKS = ["player_id", "stat"]


PlayerProps = PlayerPropTable(DB)
