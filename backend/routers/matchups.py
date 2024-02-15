from fastapi import Response, Request
from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Union, Optional

from fastapi import APIRouter
import time
import uuid


import pandas as pd

from global_implementations import constants
from helpers.db_helpers import get_matchup_gamelog
from sql_app.register.lineup import Lineups
from sql_app.register.matchup import Matchups
from sql_app.serializers.matchup import MatchupSerializer
from sql_app.serializers.matchup import MatchupReadSerializer
from sql_app.serializers.gamelog import GamelogSerializer

from typing import List

import logging

logger = logging.getLogger("main")

router = APIRouter()

############################
# ListMatchups
############################


@router.get("/", response_model=List[MatchupReadSerializer])
async def list_matchups():
    return Matchups.get_all_records()


############################
# RetrieveMatchup
############################


@router.get("/{id}", response_model=MatchupSerializer)
async def retrieve_matchup(id: str):
    matchup = Matchups.get_record(query={"id": id})

    if matchup:
        return matchup
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Matchup not found with id: {id}.",
        )


############################
# RetrieveMatchupStats
############################

import traceback


@router.get("/{id}/stats/{home_away}", response_model=List[GamelogSerializer])
async def retrieve_matchup_stats(id: str, home_away: str):
    try:
        if home_away == "home":
            matchup = get_matchup_gamelog(id=id)
        else:
            matchup = get_matchup_gamelog(id=id, home_player=False)

        return matchup
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {e}",
        )
