import logging

from fastapi import APIRouter
from nbastats.db.register import Games, Lineups
from nbastats.db.register.serializers import GameReadSerializer

logger = logging.getLogger("main")

router = APIRouter()


@router.get("/{game_id}")
def get_lineups_by_game_id(game_id: str):
    game: GameReadSerializer = Games.get_record(query={"id": game_id})  # type: ignore

    if not game:
        return {}

    home_lineup = Lineups.get_record(
        query={"game_id": game_id, "team": game.home.name.upper()}
    )
    away_lineup = Lineups.get_record(
        query={"game_id": game_id, "team": game.away.name.upper()}
    )

    if home_lineup and away_lineup:
        return {
            "home_lineup": home_lineup.model_dump(),
            "away_lineup": away_lineup.model_dump(),
        }
    else:
        return {}
