import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nbastats.webapp.routers import (
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


app = FastAPI(debug=True)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matchups.router, prefix="/matchups", tags=["matchups"])
app.include_router(gamelogs.router, prefix="/gamelogs", tags=["gamelogs"])
app.include_router(player_props.router, prefix="/player-props", tags=["player-props"])
app.include_router(
    defense_rankings.router, prefix="/defense-rankings", tags=["defense-rankings"]
)
app.include_router(career_stats.router, prefix="/career-stats", tags=["career-stats"])
app.include_router(lineups.router, prefix="/lineups", tags=["lineups"])
app.include_router(games.router, prefix="/games", tags=["games"])
app.include_router(players.router, prefix="/players", tags=["players"])


@app.get("/")
async def get_status():
    return {
        "status": True,
    }
