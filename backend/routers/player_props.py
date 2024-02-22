import pandas as pd
from fastapi import APIRouter

from sql_app.serializers.player_prop import PlayerPropSerializer
from sql_app.serializers.player_prop import ReadPlayerPropSerializer
from sql_app.serializers.player_prop import ReadPropLineSerializer
from sql_app.register.player_prop import PlayerProps
from sql_app.register.player_prop import PropLines
from sql_app.register.gamelog import Gamelogs
from typing import List

import logging

logger = logging.getLogger("main")


router = APIRouter()

############################
# GetPropsByPlayerID
############################


@router.get("/{player_id}")
async def get_props_by_player_id(player_id: str):
    player = PlayerProps.get_record(query={"player_id": player_id})

    if not player:
        print(f"No prop lines for player: {player_id}")
        return []

    lines = PropLines.filter_records(query={"player_id": player.id})  # type: ignore

    new_lines = {}
    for line in lines:
        new_lines[line.stat] = {
            "line": line.line,
            "over": line.over,
            "under": line.under,
            "over_implied": line.over_implied,
            "under_implied": line.under_implied,
        }

    return [new_lines]


@router.get("/{player_id}/hitrates")
async def get_player_hitrates(player_id: str):
    player = PlayerProps.get_record(query={"player_id": player_id})

    if not player:
        print(f"No prop lines for player: {player_id}")
        return {}

    # Get the prop lines for the given player
    lines = PropLines.filter_records(query={"player_id": player.id})  # type: ignore

    # Get player career gamelog
    career_gamelog: pd.DataFrame = Gamelogs.filter_records(
        query={"player_id": player_id}, as_df=True
    )

    if career_gamelog.empty:
        return {}

    career_gamelog = career_gamelog.dropna(subset=["G"])

    average_minutes_played = career_gamelog["MP"].mean()

    career_gamelog = career_gamelog[
        career_gamelog["MP"] >= average_minutes_played * 0.9
    ]

    career_games_played = len(career_gamelog)

    hitrates = {}
    for line in lines:
        stat_overs = career_gamelog[career_gamelog[line.stat] >= line.line]
        hitrates[line.stat] = round(
            len(stat_overs) / career_games_played * 100, ndigits=2
        )

    return hitrates
