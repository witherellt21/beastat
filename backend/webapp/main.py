from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from webapp.routers import matchups
from webapp.routers import gamelogs
from webapp.routers import player_props
from webapp.routers import defense_rankings
from webapp.routers import career_stats
from webapp.routers import lineups
from webapp.routers import games
from webapp.routers import players
from fastapi.logger import logger

from scraper.career_stats import CareerStatsScraper
from scraper.gamelog import GamelogScraper
from scraper.lineups import LineupScraper
from scraper.player_props import PlayerPropsScraper
from scraper.player_info import PlayerInfoScraper
from scraper.defense_rankings_scraper import DefenseRankingsScraper

import logging
import threading
import webapp.config as config

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


# TODO: MASSIVE work needs to be done in keeping these scrapers asynchronous in case data is missing
if config.DATA_SCRAPE.get("PlayerInfo", {}).get("status"):
    player_info_scraper = PlayerInfoScraper()
    player_info_scraper.setDaemon(True)
    player_info_scraper.start()

if config.DATA_SCRAPE.get("Lineups", {}).get("status"):
    lineup_scraper = LineupScraper()
    lineup_scraper.setDaemon(True)
    lineup_scraper.start()

if config.DATA_SCRAPE.get("CareerStats", {}).get("status"):
    career_stats_scraper = CareerStatsScraper(
        **config.DATA_SCRAPE.get("CareerStats", {}).get("options", {})
    )
    career_stats_scraper.setDaemon(True)
    career_stats_scraper.start()

if config.DATA_SCRAPE.get("PlayerProps", {}).get("status"):
    player_props_scraper = PlayerPropsScraper()
    player_props_scraper.setDaemon(True)
    player_props_scraper.start()

if config.DATA_SCRAPE.get("DefenseRankings", {}).get("status"):
    defense_rankings_scraper = DefenseRankingsScraper()
    defense_rankings_scraper.setDaemon(True)
    defense_rankings_scraper.start()

if config.DATA_SCRAPE.get("Gamelogs", {}).get("status"):
    gamelog_scraper = GamelogScraper(
        **config.DATA_SCRAPE.get("Gamelogs", {}).get("options", {})
    )
    gamelog_scraper.setDaemon(True)
    gamelog_scraper.start()


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
