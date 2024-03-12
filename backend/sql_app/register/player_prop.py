from sql_app.models.player_prop import PropLine
from sql_app.serializers.player_prop import (
    PlayerPropSerializer,
    ReadPlayerPropSerializer,
    PlayerPropTableEntrySerializer,
)


from sql_app.database import DB
from sql_app.register.base import BaseTable


class PlayerPropTable(BaseTable):
    MODEL_CLASS = PropLine
    SERIALIZER_CLASS = PlayerPropSerializer
    READ_SERIALIZER_CLASS = ReadPlayerPropSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = PlayerPropTableEntrySerializer
    PKS = ["player_id", "stat"]


PlayerProps = PlayerPropTable(DB)
