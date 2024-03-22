from base.sql_app.register import BaseTable
from nbastats.sql_app.database import DB
from nbastats.sql_app.models import PropLine
from nbastats.sql_app.serializers import (
    PlayerPropSerializer,
    PlayerPropTableEntrySerializer,
    ReadPlayerPropSerializer,
)


class PlayerPropTable(BaseTable):
    MODEL_CLASS = PropLine
    SERIALIZER_CLASS = PlayerPropSerializer
    READ_SERIALIZER_CLASS = ReadPlayerPropSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = PlayerPropTableEntrySerializer
    PKS = ["player_id", "stat"]


PlayerProps = PlayerPropTable(DB)
