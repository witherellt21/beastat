from fastapi import FastAPI, Depends
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from routers import matchups
from routers import gamelogs

import time
import threading

import pandas as pd

from helpers.db_helpers import get_matchups
from helpers.db_helpers import get_player_id

from data_scrape.career_stats import CareerStatsScraper
from data_scrape.gamelog import GamelogScraper
from data_scrape.lineups import LineupDataScraper
from data_scrape.player_info import PlayerInfoScraper
from sql_app.serializers.matchup import MatchupSerializer
from sql_app.register.matchup import Matchups

from string import ascii_lowercase

RUNNING = True


def get_player_full_gamelog(
    *, player_id: str, years_active: "list[int]"
) -> pd.DataFrame:
    # Get the players full gamelog
    full_gamelog_data = pd.DataFrame()
    for year in years_active:
        current_gamelog: GamelogScraper = GamelogScraper(player_id=player_id, year=year)
        current_gamelog_data: pd.DataFrame = current_gamelog.get_data()
        full_gamelog_data = pd.concat(
            [full_gamelog_data, current_gamelog_data], ignore_index=True
        )

    return full_gamelog_data


class BasketballRefScraper(threading.Thread):
    def __init__(self, **kwargs: dict) -> None:
        self.RUNNING: bool = True
        self.preset_matchups = kwargs.get("preset_matchups", None)
        super().__init__()

    def run(self) -> None:
        while self.RUNNING:
            matchups: list[MatchupSerializer] = (
                self.preset_matchups or Matchups.get_all_records()
            )

            for matchup in matchups:
                print(matchup)
                for player_name in [matchup.home_player, matchup.away_player]:
                    player_id = get_player_id(player_name=player_name)

                    if not player_id:
                        continue

                    try:
                        # Get the CareerStats for the given player
                        career_stats: CareerStatsScraper = CareerStatsScraper(
                            player_id=player_id
                        )
                        career_data: pd.DataFrame = career_stats.get_data()

                        # print(career_stats)
                        # Get the players active seasons from the CareerStats
                        seasons_active: list[int] = career_stats.get_active_seasons()

                        # Get the player Gamelog
                        player_gamelog: pd.DataFrame = get_player_full_gamelog(
                            player_id=player_id, years_active=seasons_active
                        )
                        player_gamelog["player_name"] = player_name
                    except Exception as e:
                        print(e)

            time.sleep(1)
        print("No longer scraping bref.")


class InfoScraper(threading.Thread):
    def __init__(self) -> None:
        self.RUNNING: bool = True
        super().__init__()

    def run(self) -> None:
        # Get all of the active players by last initial
        for letter in ascii_lowercase:
            # TODO: idea - create an EXPECTED_COLUMNS variable for ABD and initialize the data using this. This would save an empty dataframe
            if letter == "x":
                continue

            player_info = PlayerInfoScraper(last_initial=letter)
            player_info.get_data()


lineup_scraper = LineupDataScraper()
lineup_scraper.start()
# bref_scraper = BasketballRefScraper(
#     preset_matchups=[Matchups.get_record(query={"game_id": 4, "position": "SF"})]
# )
bref_scraper = BasketballRefScraper()
bref_scraper.start()
# info_scraper = InfoScraper()
# info_scraper.start()
# bref_thread = threading.Thread(target=scrape_bref)
# bref_thread.start()

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


@app.get("/")
async def get_status():
    return {
        "status": True,
    }
