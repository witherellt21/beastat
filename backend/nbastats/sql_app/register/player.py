import logging
from typing import Optional

import pandas as pd
from core.sql_app.register import BaseTable
from core.util.strings import find_closest_match
from nbastats.sql_app.models import Player, PropLine
from nbastats.sql_app.serializers import PlayerSerializer, ReadPlayerSerializer
from playhouse.shortcuts import model_to_dict

logger = logging.getLogger("main")


class PlayerTable(BaseTable):
    MODEL_CLASS = Player
    SERIALIZER_CLASS = PlayerSerializer
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

    def get_player_id_from_name(self, player_name: str) -> Optional[str]:
        # Try to get the player's id given their name
        player: PlayerSerializer = self.get_record(query={"name": player_name})  # type: ignore

        # if no player found, try to get the closes match to their name
        if not player:
            # player_name = PLAYER_NICKNAMES.get(player_name, player_name)

            player_names: list[str] = self.get_column_values(column="name")

            player_name_match: Optional[str] = find_closest_match(
                value=player_name, search_list=player_names
            )

            # if no match found, return None
            if not player_name_match:
                logger.warning(f"Could not find player id for {player_name}")
                return None

            # Get the player id for the closest name match
            player: PlayerSerializer = self.get_record(query={"name": player_name_match})  # type: ignore

        return player.id
