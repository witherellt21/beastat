from fastapi import Response, Request
from fastapi import Depends, FastAPI, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Union, Optional

from fastapi import APIRouter
import time
import uuid


import pandas as pd

from global_implementations import constants
from helpers.db_helpers import get_matchups
from sql_app.register.lineup import Lineups
from sql_app.serializers.lineup import MatchupSerializer

from typing import List

router = APIRouter()

############################
# GetMatchups
############################


@router.get("/", response_model=List[MatchupSerializer])
async def retrieve_matchups():
    return get_matchups()
