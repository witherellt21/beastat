from sql_app.models.player_prop import PropLine
from sql_app.serializers.player_prop import PropLineSerializer
from sql_app.serializers.player_prop import ReadPropLineSerializer

from sql_app.database import DB
from sql_app.register.base import BaseTable


class PropLineTable(BaseTable):
    MODEL_CLASS = PropLine
    SERIALIZER_CLASS = PropLineSerializer
    READ_SERIALIZER_CLASS = ReadPropLineSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = PropLineSerializer
    PKS = ["player_id", "stat"]


PropLines = PropLineTable(DB)
