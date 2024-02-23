import pandas as pd
from fastapi import APIRouter

from helpers.db_helpers import get_matchup_gamelog_by_player_id
from sql_app.serializers.player_prop import PlayerPropSerializer
from sql_app.serializers.player_prop import ReadPlayerPropSerializer
from sql_app.serializers.player_prop import ReadPropLineSerializer
from sql_app.register.player_prop import PlayerProps
from sql_app.register.player_prop import PropLines
from sql_app.register.gamelog import Gamelogs
from typing import List, Optional

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

    lines: list[ReadPropLineSerializer] = PropLines.filter_records(query={"player_id": player.id})  # type: ignore

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
async def get_player_hitrates(
    player_id: str,
    query: str = "",
    startyear: Optional[str] = None,
    matchups_only: bool = False,
):
    player = PlayerProps.get_record(query={"player_id": player_id})

    if not player:
        print(f"No prop lines for player: {player_id}")
        return {}

    # Get the prop lines for the given player
    lines: list[ReadPropLineSerializer] = PropLines.filter_records(query={"player_id": player.id})  # type: ignore

    # Filter gamelogs according to the matchup only query
    if matchups_only:
        gamelog: pd.DataFrame = get_matchup_gamelog_by_player_id(player_id=player_id)
    else:
        gamelog: pd.DataFrame = Gamelogs.filter_records(
            query={"player_id": player_id}, as_df=True
        )

    print(gamelog)

    if gamelog.empty:
        return {}

    gamelog = gamelog.dropna(subset=["G"])

    # average_minutes_played = career_gamelog["MP"].mean()

    # career_gamelog = career_gamelog[
    #     career_gamelog["MP"] >= average_minutes_played * 0.9
    # ]
    filtered_gamelog: pd.DataFrame = gamelog.query(query)
    filtered_gamelog = filtered_gamelog.fillna("")

    if startyear:
        try:
            filtered_gamelog = filtered_gamelog[
                filtered_gamelog["Date"].dt.year >= int(startyear)
            ]
        except Exception as e:
            print(e)

    total_number_of_games = len(filtered_gamelog)

    hitrates = {}
    for line in lines:
        stat_overs = filtered_gamelog[filtered_gamelog[line.stat] >= line.line]
        hitrates[line.stat] = round(
            len(stat_overs) / total_number_of_games * 100, ndigits=2
        )

    return hitrates
