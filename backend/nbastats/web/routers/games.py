import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from nbastats.db.register import Games
from nbastats.db.register.serializers import GameSerializer

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


@router.get("/{team}", response_model=GameSerializer)
def get_team_game(team: str):
    games = Games.filter_by_datetime(min_datetime=datetime.today(), as_df=True)

    REMAP = {"PHO": "PHX"}
    team = REMAP.get(team, team)

    games = games[(games["home"] == team) | (games["away"] == team)]

    if games.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current games found for the requested team.",
        )

    # return {}
    return GameSerializer(**games.to_dict(orient="records")[0])
