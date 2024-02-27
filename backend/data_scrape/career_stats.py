# Aliases
import numpy as np
import pandas as pd

# Module imports
import logging
import os
import re

# Package imports
from data_scrape.abstract_base_scraper import AbstractBaseScraper
from data_scrape.test.main_tester_functions import test_scraper_thread
from helpers.string_helpers import convert_season_to_year
from sql_app.register.career_stats import CareerStatss
from sql_app.register.matchup import Matchups
from sql_app.register.player_info import PlayerInfos

from typing import Unpack, Literal, TypedDict, Iterable, Optional


IS_SEASON = re.compile(r"^\d{4}")


class CareerStatsScraper(AbstractBaseScraper):
    class Kwargs(TypedDict, total=False):
        identifier_source: Literal["matchups_only", "all"]

    STAT_AUGMENTATIONS = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
    }

    TRANSFORMATIONS = {"Season": lambda season: convert_season_to_year(season=season)}

    _exception_msgs = {
        "load_data": f"Error reading saved player overview from csv.",
        "download_data": f"Error fetching (http) player overview from html.",
    }
    FILTERS = [lambda dataframe: bool(IS_SEASON.match(dataframe["Season"]))]

    RENAME_COLUMNS = {
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "2P": "TWP",
        "2PA": "TWPA",
        "2P%": "TWP_perc",
        "eFG%": "eFG_perc",
        "FT%": "FT_perc",
    }
    QUERY_SAVE_COLUMNS = ["player_id"]

    TABLE = CareerStatss

    LOG_LEVEL = logging.WARNING

    def __init__(self, **kwargs: Unpack[Kwargs]):

        self.identifier_source: Literal["matchups_only", "all"] = kwargs.pop(
            "identifier_source", "matchups_only"
        )

        super().__init__(**kwargs)

    @property
    def download_url(self):
        return "http://www.basketball-reference.com/players/{player_last_initial}/{player_id}.html"

    def select_dataset_from_html_tables(
        self, *, datasets: list[pd.DataFrame]
    ) -> pd.DataFrame:
        # Filter the dataframe to get the career stats dataframe
        season_stat_datasets: list[pd.DataFrame] = list(
            filter(lambda dataset: "Season" in dataset.columns, datasets)
        )

        if not season_stat_datasets:
            raise Exception(
                f"Could not find dataset with 'Seasons' column in \n {datasets}"
            )

        return season_stat_datasets[0]

    def get_query_set(self) -> Optional[list[dict[str, str]]]:
        player_ids: Iterable[str] = []

        if self.identifier_source == "matchups_only":
            matchups = Matchups.get_all_records(as_df=True)

            home_players = matchups["home_player_id"].unique()
            away_players = matchups["away_player_id"].unique()

            if len(home_players) == 0 or len(away_players) == 0:
                return []

            player_ids = np.concatenate(
                (
                    matchups["home_player_id"].unique(),
                    matchups["away_player_id"].unique(),
                )
            )

        elif self.identifier_source == "all":
            all_players = PlayerInfos.get_all_records(as_df=True)

            if not all_players.empty:
                player_ids = list(all_players["player_id"].values)
            else:
                return []

        return [
            {"player_last_initial": player_id[0], "player_id": player_id}
            for player_id in player_ids
        ]

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = super().clean(data=data)

        data = data.dropna(subset="Season")
        data = data.dropna(subset="G")

        data["Awards"] = data["Awards"].fillna("")

        return data

    def is_cached(self, *, query: dict[str, str]) -> bool:
        player_id = query.get("player_id")
        player_info = PlayerInfos.get_record(query={"player_id": player_id})
        start_year = player_info.active_from  # type: ignore
        end_year = player_info.active_to  # type: ignore

        for year in range(start_year, end_year + 1):
            existing_data = CareerStatss.get_record(
                query={"player_id": player_id, "Season": float(year)}
            )
            existing_as_int = CareerStatss.get_record(
                query={"player_id": player_id, "Season": int(year)}
            )

            if not existing_data or existing_as_int:
                return False

        return True


if __name__ == "__main__":
    player_info: CareerStatsScraper = CareerStatsScraper()
    data = player_info.get_data(
        query={"player_id": "bogdabo01", "player_last_initial": "b"}
    )
    # print(data)
    # test_scraper_thread(scraper_class=CareerStatsScraper)
