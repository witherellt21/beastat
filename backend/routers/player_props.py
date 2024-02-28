import pandas as pd
from fastapi import APIRouter, Query, Depends

from helpers.db_helpers import get_matchup_gamelog_by_player_id, filter_gamelog
from sql_app.serializers.player_prop import PlayerPropSerializer
from sql_app.serializers.player_prop import ReadPlayerPropSerializer
from sql_app.serializers.player_prop import ReadPropLineSerializer
from sql_app.register.player_prop import PlayerProps
from sql_app.register.player_prop import PropLines
from sql_app.register.gamelog import Gamelogs
from typing import List, Optional
from pydantic import BaseModel

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


class GamelogQuery(BaseModel):
    query: Optional[str] = None
    limit: int = 50
    matchups_only: bool = False
    startyear: int = 2024


@router.get("/{player_id}/hitrates")
async def get_player_hitrates(
    player_id: str,
    query: GamelogQuery = Depends(),
    without_teammates: list[str] = Query(None),
    with_teammates: list[str] = Query(None),
):
    player = PlayerProps.get_record(query={"player_id": player_id})

    if not player:
        print(f"No prop lines for player: {player_id}")
        return {}

    # Get the prop lines for the given player
    lines: list[ReadPropLineSerializer] = PropLines.filter_records(query={"player_id": player.id})  # type: ignore

    gamelog = filter_gamelog(
        player_id=player_id,
        query=query.query,
        startyear=query.startyear,
        matchups_only=query.matchups_only,
        limit=query.limit,
        without_teammates=without_teammates,
        with_teammates=with_teammates,
    )

    if gamelog.empty:
        return {}

    total_number_of_games = len(gamelog)

    hitrates = {}
    for line in lines:
        stat_overs = gamelog[gamelog[line.stat] >= line.line]
        hitrates[line.stat] = round(
            len(stat_overs) / total_number_of_games * 100, ndigits=2
        )

    return hitrates
