from fastapi import HTTPException, status
from fastapi import APIRouter
import logging

from sql_app.register.lineup import Lineups
from sql_app.register.game import Games
from sql_app.serializers.game import GameSerializer

logger = logging.getLogger("main")

router = APIRouter()


@router.get("/{game_id}")
def get_lineups_by_game_id(game_id: str):
    game: GameSerializer = Games.get_record(query={"id": game_id})  # type: ignore

    print(game)

    if not game:
        return {}

    home_lineup = Lineups.get_record(
        query={"game_id": game_id, "team": game.home.upper()}
    )
    away_lineup = Lineups.get_record(
        query={"game_id": game_id, "team": game.away.upper()}
    )

    print(home_lineup)
    print(away_lineup)

    if home_lineup and away_lineup:
        return {
            "home_lineup": home_lineup.model_dump(),
            "away_lineup": away_lineup.model_dump(),
        }
    else:
        return {}
