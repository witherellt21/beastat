from fastapi import HTTPException, status
from fastapi import APIRouter
import logging

from sql_app.register.career_stats import CareerStatss

logger = logging.getLogger("main")

router = APIRouter()


@router.get("/{player_id}/season/{year}")
def get_player_averages_for_season(player_id: str, year: int):
    averages = CareerStatss.get_record(
        query={"player_id": player_id, "Season": float(year)}
    )

    if averages:
        return averages.model_dump()
    else:
        return {}
