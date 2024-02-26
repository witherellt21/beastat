from fastapi import HTTPException, status
from fastapi import APIRouter
import logging

from sql_app.register.lineup import Lineups

logger = logging.getLogger("main")

router = APIRouter()


@router.get("/{game_id}")
def get_lineups_by_game_id(game_id: str):
    home_lineup = Lineups.get_record(query={"game_id": game_id, "home": True})
    away_lineup = Lineups.get_record(query={"game_id": game_id, "home": False})

    if home_lineup and away_lineup:
        return {
            "home_lineup": home_lineup.model_dump(),
            "away_lineup": away_lineup.model_dump(),
        }
    else:
        return {}
