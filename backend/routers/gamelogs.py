from fastapi import HTTPException, status
from fastapi import APIRouter, Depends, Query

import pandas as pd
from typing import Optional, Unpack, List
from helpers.db_helpers import get_matchup_gamelog_by_player_id, filter_gamelog
from sql_app.register.gamelog import Gamelogs
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

import logging
import exceptions

logger = logging.getLogger("main")

router = APIRouter()


class GamelogQuery(BaseModel):
    query: Optional[str] = None
    limit: int = 50
    matchups_only: bool = False
    startyear: int = 2024
    # without_teammates: List[str] = Query([])


############################
# GetGamelogByPlayerID
############################


@router.get("/{player_id}")
async def get_gamelog_by_player_id(
    player_id: str,
    query: GamelogQuery = Depends(),
    without_teammates: list[str] = Query(None),
    with_teammates: list[str] = Query(None),
):
    print(with_teammates)
    try:
        gamelog = filter_gamelog(
            player_id=player_id,
            query=query.query,
            startyear=query.startyear,
            matchups_only=query.matchups_only,
            limit=query.limit,
            without_teammates=without_teammates,
            with_teammates=with_teammates,
        )

        print(gamelog)

        if not gamelog.empty:
            return gamelog.to_dict(orient="records")
        else:
            return []

    except exceptions.DBNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving the player's gamelogs. {e}",
        )
