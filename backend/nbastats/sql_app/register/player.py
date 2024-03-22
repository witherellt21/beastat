import logging

import pandas as pd
from base.sql_app.register import BaseTable
from nbastats.sql_app.database import DB
from nbastats.sql_app.models import Player, PropLine
from nbastats.sql_app.serializers import (
    PlayerSerializer,
    PlayerTableEntrySerializer,
    ReadPlayerSerializer,
)
from playhouse.shortcuts import model_to_dict

logger = logging.getLogger("main")


class PlayerTable(BaseTable):
    MODEL_CLASS = Player
    SERIALIZER_CLASS = PlayerSerializer
    TABLE_ENTRY_SERIALIZER_CLASS = PlayerTableEntrySerializer
    READ_SERIALIZER_CLASS = ReadPlayerSerializer
    PKS = ["id"]

    def get_with_prop_lines(self, *, query: dict):
        player = Player.select().join(PropLine).dicts()
        return player

    def get_players_with_last_initial(self, *, last_initial: str) -> pd.DataFrame:
        query = Player.select().where(Player.id.startswith(last_initial))

        records = []
        for record in query:
            records.append(model_to_dict(record, recurse=False))

        data = pd.DataFrame(records)

        return data.set_index(self.model_class._meta.primary_key.name) if not data.empty else data  # type: ignore


# Players = PlayerTable(DB)
