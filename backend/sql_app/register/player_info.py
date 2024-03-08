from sql_app.models.player_info import Player
from sql_app.serializers.player_info import (
    PlayerSerializer,
    PlayerTableEntrySerializer,
)

from sql_app.database import DB
from sql_app.register.base import BaseTable
from playhouse.shortcuts import model_to_dict

from sql_app.models.player_prop import PropLine

import logging

logger = logging.getLogger("main")


class PlayerTable(BaseTable):
    MODEL_CLASS = Player
    SERIALIZER_CLASS = PlayerSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = PlayerTableEntrySerializer
    PKS = ["id"]

    def get_with_prop_lines(self, *, query: dict):
        player = Player.select().join(PropLine).dicts()
        return player


Players = PlayerTable(DB)
