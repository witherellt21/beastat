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

from typing import Unpack, Literal, TypedDict, Iterable


IS_SEASON = re.compile(r"^\d{4}")


# def convert_seasons_to_years(*, dataset: pd.DataFrame, id_from_column: str):
#     for index, row in dataset.iterrows():
#         season: str = row[id_from_column]
#         if IS_SEASON.match(season):
#             dataset.loc[index, id_from_column] = str(
#                 convert_season_to_year(season=season)
#             )

#     return dataset[id_from_column]


# def convert_season_to_years(*, season: str) -> str:
#     if IS_SEASON.match(season):
#         dataset.loc[index, id_from_column] = str(convert_season_to_year(season=season))


class CareerStatsScraper(AbstractBaseScraper):
    class Kwargs(TypedDict, total=False):
        identifier_source: Literal["matchups_only", "all"]

    STAT_AUGMENTATIONS = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
        # "Season": lambda dataset: convert_seasons_to_years(
        #     dataset=dataset, id_from_column="Season"
        # ),
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

    LOG_LEVEL = logging.INFO

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
        return season_stat_datasets[0]

    def get_query_set(self) -> list[dict[str, str]]:
        player_ids: Iterable[str] = []

        if self.identifier_source == "matchups_only":
            matchups = Matchups.get_all_records(as_df=True)

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

    def cache_data(self, *, data: pd.DataFrame) -> None:
        print(data)


if __name__ == "__main__":
    player_info: CareerStatsScraper = CareerStatsScraper()
    data = player_info.get_data(
        query={"player_id": "jamesle01", "player_last_initial": "j"}
    )
    # print(data)
    # test_scraper_thread(scraper_class=CareerStatsScraper)
