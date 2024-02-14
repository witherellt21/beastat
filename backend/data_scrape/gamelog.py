import logging
import os

import numpy as np
import pandas as pd

from data_scrape.abstract_base_scraper import AbstractBaseScraper
from helpers.db_helpers import get_player_id
from helpers.db_helpers import get_player_active_seasons
from sql_app.register.gamelog import Gamelogs
from sql_app.register.matchup import Matchups

from exceptions import NoDataFoundException


def convert_minutes_to_float(time: str):
    if not isinstance(time, str):
        return time

    minutes, seconds = time.split(":")
    result = int(minutes) + round(int(seconds) / 60, ndigits=1)
    return result


class GamelogScraper(AbstractBaseScraper):
    RENAME_COLUMNS = {
        "Unnamed: 7": "streak",
        "FT%": "FT_perc",
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "+/-": "plus_minus",
    }
    DROP_COLUMNS: "list[str]" = ["Unnamed: 5"]
    TRANSFORMATIONS = {"MP": lambda x: convert_minutes_to_float(x)}
    COLUMN_TYPES: "dict[str:str]" = {
        "Tm": "str",
        "Opp": "str",
        "PTS": "float",
        "GmSc": "float",
        "G": "float",
        "GS": "float",
        "MP": "float",
        "AST": "float",
        "TRB": "float",
        "FT": "float",
        "THPA": "float",
        "THP": "float",
        "FGA": "float",
        "FG": "float",
        "STL": "float",
        "FG_perc": "float",
        "THP_perc": "float",
        "plus_minus": "float",
        "FTA": "float",
        "FT_perc": "float",
        "ORB": "float",
        "DRB": "float",
        "BLK": "float",
        "TOV": "float",
        "PF": "float",
        "GmSc": "float",
        "plus_minus": "float",
    }
    DATETIME_COLUMNS: "dict[str:str]" = {"Date": "%Y-%m-%d"}
    STAT_AUGMENTATIONS: "dict[str:str]" = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
    }
    TABLE = Gamelogs
    LOG_LEVEL = logging.INFO

    @property
    def download_url(self):
        return "http://www.basketball-reference.com/players/{}/{}/gamelog/{}"

    def format_url_args(self, *, identifier: str) -> "list[str]":
        player_id, year = identifier
        return [player_id[0], player_id, year]

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        # TODO: This filter seems awfully presumptuous, maybe we should change it at some point
        return list(filter(lambda x: x.shape[1] == 30, datasets))[0]

    def get_identifiers(self) -> "list[str|tuple[str]]":
        # TODO: There has to be a faster way to do this. Without extend and iteration
        matchups = Matchups.get_all_records(as_df=True)

        players = np.concatenate(
            (matchups["home_player_id"].unique(), matchups["away_player_id"].unique())
        )

        identifiers = []
        for player in players:
            try:
                active_seasons = get_player_active_seasons(player_id=player)

                identifiers.extend(
                    list(map(lambda year: (player, year), active_seasons))
                )
            except NoDataFoundException:
                continue

        return identifiers

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # TODO: We can create class attributes for removing rows and setting the index
        # Remove extra column rows from dataset
        data: pd.DataFrame = data[data["Rk"] != "Rk"]

        # Reset the index to all games where player was rostered this season, including Inactive games
        data: pd.DataFrame = data.set_index("Rk")

        return super().clean(data=data)

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = super().configure_data(data=data)
        # TODO: Can probably move this to base
        return data.fillna(np.nan).replace([np.nan], [None])

    def download_data(self, *, url_args: "list[str]" = []) -> pd.DataFrame:
        # TODO: we shouln't make augmentations here. So we will need to fix the SAVE_IDENTIFIER_AS attribute to a dict and support lists
        data = super().download_data(url_args=url_args)
        data["player_id"] = url_args[1]
        return data

    def cache_data(self, *, data: pd.DataFrame) -> None:
        self.logger.debug(data)
        pass


if __name__ == "__main__":

    gamelog = GamelogScraper()
    gamelog.get_data(identifier=("jamesle01", 2023))
