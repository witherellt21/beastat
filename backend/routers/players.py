import logging
import pandas as pd
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional
from sql_app.serializers.player_info import PlayerSerializer
from sql_app.register.player_info import Players
from sql_app.models.player_info import Player
from sql_app.models.player_prop import PropLine
from playhouse.shortcuts import model_to_dict

router = APIRouter()


@router.get("/{player_id}")
def get_player(player_id: str):
    # player = Players.get_with_prop_lines(query={"id": player_id})
    # return player
    player = (
        Player.select(Player, PropLine).join(PropLine).where(Player.id == player_id)
    )

    for p in player:
        print(p)
        as_dict = model_to_dict(p)
        print(as_dict)

    return as_dict
