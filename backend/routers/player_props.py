import pandas as pd
from fastapi import APIRouter, Query, Depends

from helpers.db_helpers import (
    get_matchup_gamelog_by_player_id,
    filter_gamelog,
    GamelogQuery,
)
from sql_app.serializers.player_prop import ReadPropLineSerializer
from sql_app.register.player_prop import PropLines
from sql_app.register.gamelog import Gamelogs
from typing import List, Optional
from pydantic import BaseModel

import logging

logger = logging.getLogger("main")


router = APIRouter()


############################
# ListAllActiveProps
############################


@router.get("/", response_model=list[ReadPropLineSerializer])
async def list_all_active_props():
    player_props = PropLines.get_all_records()
    return player_props

    # if not player_props:
    #     print(f"No prop lines for player: {player_id}")
    #     return []

    # lines: list[ReadPropLineSerializer] = PropLines.filter_records(query={"player_id": player.id})  # type: ignore

    # new_lines = {}
    # for line in lines:
    #     new_lines[line.stat] = {
    #         "line": line.line,
    #         "over": line.over,
    #         "under": line.under,
    #         "over_implied": line.over_implied,
    #         "under_implied": line.under_implied,
    #     }

    # return [new_lines]


############################
# GetPropsByPlayerID
############################


@router.get("/{player_id}")
async def get_props_by_player_id(player_id: str):
    lines: list[ReadPropLineSerializer] = PropLines.filter_records(query={"player_id": player_id})  # type: ignore

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


@router.post("/{player_id}/hitrates")
async def get_player_hitrates(
    player_id: str,
    query: GamelogQuery,
):
    lines: list[ReadPropLineSerializer] = PropLines.filter_records(query={"player_id": player_id})  # type: ignore

    if not lines:
        print(f"No prop lines for player: {player_id}")
        return {}

    gamelog = filter_gamelog(player_id=player_id, query=query)

    if gamelog.empty:
        return {}

    total_number_of_games = len(gamelog)

    hitrates = {}
    for limit in [total_number_of_games, 30, 20, 10, 5, 3]:
        hitrates_per_limit = {}
        for line in lines:
            sublog = gamelog.tail(limit)
            stat_overs = sublog[sublog[line.stat] >= line.line]
            hitrates_per_limit[line.stat] = round(
                len(stat_overs) / len(sublog) * 100, ndigits=2
            )
        identifier = "all" if limit == total_number_of_games else f"last_{limit}"
        hitrates[identifier] = hitrates_per_limit

    return hitrates
