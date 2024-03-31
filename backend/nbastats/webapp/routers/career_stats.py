import logging

from fastapi import APIRouter, HTTPException, status
from nbastats.sql_app.register import SeasonAveragess

logger = logging.getLogger("main")

router = APIRouter()


@router.get("/{player_id}/season/{year}")
def get_player_averages_for_season(player_id: str, year: int):
    averages = SeasonAveragess.get_record(
        query={"player_id": player_id, "Season": float(year)}
    )

    if averages:
        return averages.model_dump()
    else:
        return {}
