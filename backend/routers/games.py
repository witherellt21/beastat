import logging
import pandas as pd
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from typing import List, Optional

from sql_app.serializers import GameSerializer
from sql_app.register import Games

logger = logging.getLogger("main")

router = APIRouter()


@router.get("/", response_model=list[GameSerializer])
def list_games():
    games = Games.get_all_records()
    return games


@router.get("/today", response_model=list[GameSerializer])
def list_todays_games():
    games = Games.filter_by_datetime(min_datetime=datetime.today())
    return games
