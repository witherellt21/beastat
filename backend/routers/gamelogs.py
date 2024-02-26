from fastapi import HTTPException, status
from fastapi import APIRouter

import pandas as pd
from typing import Optional, Unpack
from helpers.db_helpers import get_matchup_gamelog_by_player_id, filter_gamelog
from sql_app.register.gamelog import Gamelogs
from pydantic import BaseModel

import logging

logger = logging.getLogger("main")

router = APIRouter()


class GamelogQuery(BaseModel):
    query: Optional[str] = None
    limit: Optional[int] = None
    matchups_only: Optional[bool] = False
    startyear: Optional[int] = None


############################
# GetGamelogByPlayerID
############################


@router.get("/{id}")
async def get_gamelog_by_player_id(
    id: str,
    query: str = "",
    startyear: Optional[str] = None,
    matchups_only: bool = False,
    limit: Optional[int] = None,
):
    try:
        gamelog = filter_gamelog(
            player_id=id,
            query=query,
            startyear=startyear,
            matchups_only=matchups_only,
            limit=limit,
        )

        if not gamelog.empty:
            return gamelog.to_dict(orient="records")
        else:
            return []

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error retrieving the player's gamelogs. {e}",
        )
