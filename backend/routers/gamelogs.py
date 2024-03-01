import traceback
from fastapi import HTTPException, status
from fastapi import APIRouter, Depends, Query

import pandas as pd
from typing import Optional, Unpack, List
from helpers.db_helpers import (
    get_matchup_gamelog_by_player_id,
    filter_gamelog,
    GamelogQuery,
)
from sql_app.register.gamelog import Gamelogs
from sql_app.register.career_stats import CareerStatss
from global_implementations import constants
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

import logging
import exceptions

logger = logging.getLogger("main")

router = APIRouter()


# class GamelogQuery(BaseModel):
#     query: Optional[str] = None
#     limit: int = 50
#     matchups_only: bool = False
#     startyear: int = 2024
#     # without_teammates: List[str] = Query([])


############################
# GetGamelogByPlayerID
############################


@router.post("/{player_id}")
async def get_gamelog_by_player_id(
    player_id: str,
    query: GamelogQuery,
):
    try:
        gamelog = filter_gamelog(player_id=player_id, query=query)

        if gamelog.empty:
            return {"gamelog": [], "averages": []}

        last_30 = gamelog.tail(30)
        last_30_avg = last_30.mean(numeric_only=True).to_dict()
        last_10 = gamelog.tail(10)
        last_10_avg = last_10.mean(numeric_only=True).to_dict()
        last_3 = gamelog.tail(3)
        last_3_avg = last_3.mean(numeric_only=True).to_dict()

        last_30_avg["Season"] = "Last 30"
        last_10_avg["Season"] = "Last 10"
        last_3_avg["Season"] = "Last 3"

        last_30_avg["G"] = 30
        last_10_avg["G"] = 10
        last_3_avg["G"] = 3

        last_30_avg["GS"] = last_30["GS"].sum()
        last_10_avg["GS"] = last_10["GS"].sum()
        last_3_avg["GS"] = last_3["GS"].sum()

        career_averages = CareerStatss.get_record(
            query={"player_id": player_id, "Season": float(constants.CURRENT_SEASON)}
        )

        career_averages = career_averages.model_dump() if career_averages else {}
        gamelogs = gamelog.to_dict(orient="records") if not gamelog.empty else []

        return {
            "gamelog": gamelogs,
            "averages": [last_30_avg, last_10_avg, last_3_avg, career_averages],
        }

    except exceptions.DBNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving the player's gamelogs. {e}",
        )
