from data_scrape import lineups
import time
import threading

import pandas as pd

from helpers.db_helpers import get_player_id

from data_scrape.career_stats import CareerStatsScraper
from data_scrape.gamelog import GamelogScraper


RUNNING = True


def get_player_full_gamelog(*, player_id: str, years_active: list[int]) -> pd.DataFrame:
    # Get the players full gamelog
    full_gamelog_data = pd.DataFrame()
    for year in years_active:
        current_gamelog: GamelogScraper = GamelogScraper(player_id=player_id, year=year)
        current_gamelog_data: pd.DataFrame = current_gamelog.get_data()
        full_gamelog_data = pd.concat(
            [full_gamelog_data, current_gamelog_data], ignore_index=True
        )

    return full_gamelog_data


def scrape_bref():
    while RUNNING:
        matchups: list[tuple[str, str]] = get_matchups()

        for matchup in matchups:
            print(matchup)
            for player_name in matchup:
                player_id = get_player_id(player_name=player_name)

                # Get the CareerStats for the given player
                career_stats: CareerStatsScraper = CareerStatsScraper(
                    player_id=player_id
                )
                career_data: pd.DataFrame = career_stats.get_data()

                # Get the players active seasons from the CareerStats
                seasons_active: list[int] = career_stats.get_active_seasons()

                # Get the player Gamelog
                player_gamelog: pd.DataFrame = get_player_full_gamelog(
                    player_id=player_id, years_active=seasons_active
                )
                player_gamelog["player_name"] = player_name

        time.sleep(1)
    print("No longer scraping bref.")


lineup_thread = threading.Thread(target=lineups.main)
lineup_thread.start()

bref_thread = threading.Thread(target=scrape_bref)
bref_thread.start()

start = time.time()
while time.time() - start < 10:
    time.sleep(0.1)

lineups.RUNNING = False
RUNNING = False
