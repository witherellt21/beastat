from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import matchups
from routers import gamelogs

from data_scrape.career_stats import CareerStatsScraper
from data_scrape.gamelog import GamelogScraper
from data_scrape.lineups import LineupDataScraper
from data_scrape.player_props import PlayerPropsScraper

# TODO: MASSIVE work needs to be done in keeping these scrapers asynchronous in case data is missing
lineup_scraper = LineupDataScraper()
lineup_scraper.start()

# career_stats_scraper = CareerStatsScraper()
# career_stats_scraper.start()

player_props_scraper = PlayerPropsScraper()
player_props_scraper.start()

# # player_info_scraper = PlayerInfoScraper()
# # player_info_scraper.start()
gamelog_scraper = GamelogScraper()
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
app.include_router(gamelogs.router, prefix="/player-props", tags=["player-props"])


@app.get("/")
async def get_status():
    return {
        "status": True,
    }
