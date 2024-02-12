from fastapi import Response, Request
from fastapi import Depends, FastAPI, HTTPException, status
from typing import List

from fastapi import APIRouter

import pandas as pd

from sql_app.register.gamelog import Gamelogs
from sql_app.serializers.gamelog import GamelogSerializer

from typing import List

router = APIRouter()

############################
# GetGamelogByPlayerID
############################


@router.get("/{id}", response_model=List[GamelogSerializer])
async def get_gamelog_by_player_id(id: str):
    try:
        return Gamelogs.filter_records(player_id=id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error retrieving the player's gamelogs. {e}",
        )