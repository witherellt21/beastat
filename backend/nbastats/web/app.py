import logging

from fastapi import APIRouter
from nbastats.web.routers import (
    career_stats,
    defense_rankings,
    gamelogs,
    games,
    lineups,
    matchups,
    player_props,
    players,
)

main_formatter = logging.Formatter(
    "[{levelname:^10}] [ {asctime} ] [{threadName:^20}]  {message}",
    "%I:%M:%S %p",
    style="{",
)

main_stream_handler = logging.StreamHandler()
main_stream_handler.setFormatter(main_formatter)

main_logger = logging.getLogger("main")
main_logger.setLevel(logging.DEBUG)
main_logger.addHandler(main_stream_handler)

router = APIRouter()

router.include_router(matchups.router, prefix="/matchups", tags=["matchups"])
router.include_router(gamelogs.router, prefix="/gamelogs", tags=["gamelogs"])
router.include_router(
    player_props.router, prefix="/player-props", tags=["player-props"]
)
router.include_router(
    defense_rankings.router, prefix="/defense-rankings", tags=["defense-rankings"]
)
router.include_router(
    career_stats.router, prefix="/career-stats", tags=["career-stats"]
)
router.include_router(lineups.router, prefix="/lineups", tags=["lineups"])
router.include_router(games.router, prefix="/games", tags=["games"])
router.include_router(players.router, prefix="/players", tags=["players"])


@router.get("/")
async def get_status():
    return {
        "status": True,
    }
