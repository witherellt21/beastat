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

IS_SEASON = re.compile("^\d{4}")


def convert_seasons_to_years(*, dataset: pd.DataFrame, id_from_column: str):
    for index, row in dataset.iterrows():
        season: str = row[id_from_column]
        if IS_SEASON.match(season):
            dataset.loc[index, id_from_column] = str(
                convert_season_to_year(season=season)
            )

    return dataset[id_from_column]


class CareerStatsScraper(AbstractBaseScraper):
    COLUMN_TYPES: "dict[str:str]" = {
        "Season": "str",
        "Tm": "str",
        "PTS": "float",
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
        "TWP": "float",
        "TWPA": "float",
        "TWP_perc": "float",
        "eFG_perc": "float",
        "FTA": "float",
        "FT_perc": "float",
        "ORB": "float",
        "DRB": "float",
        "AST": "float",
        "STL": "float",
        "BLK": "float",
        "TOV": "float",
        "PF": "float",
        "Awards": "str",
        "Age": "float",
        "Lg": "str",
        "Pos": "str",
        "G": "int",
        "GS": "int",
        "MP": "float",
    }

    STAT_AUGMENTATIONS: "dict[str:str]" = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
        "Season": lambda dataset: convert_seasons_to_years(
            dataset=dataset, id_from_column="Season"
        ),
    }

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

    TABLE = CareerStatss
    LOG_LEVEL = logging.INFO

    @property
    def download_url(self):
        return "http://www.basketball-reference.com/players/{}/{}.html"

    def format_url_args(self, *, identifier: str) -> "list[str]":
        return [identifier[0], identifier]

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        # Filter the dataframe to get the career stats dataframe
        season_stat_datasets: list[pd.DataFrame] = list(
            filter(lambda dataset: "Season" in dataset.columns, datasets)
        )
        return season_stat_datasets[0]

    def get_identifiers(self) -> "list[str | tuple[str]]":
        matchups = Matchups.get_all_records(as_df=True)

        player_ids = np.concatenate(
            (matchups["home_player_id"].unique(), matchups["away_player_id"].unique())
        )
        return list(player_ids)

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = super().clean(data=data)

        data = data.dropna(subset="Season")
        data = data.dropna(subset="G")

        data["Awards"] = data["Awards"].fillna("")

        return data

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = super().configure_data(data=data)
        data = data.fillna(np.nan).replace([np.nan], [None])
        return data

    def download_data(self, *, url_args: "list[str]" = []) -> pd.DataFrame:
        # TODO: we shouln't make augmentations here. So we will need to fix the SAVE_IDENTIFIER_AS attribute to a dict and support lists
        data = super().download_data(url_args=url_args)
        data["player_id"] = url_args[1]
        return data


if __name__ == "__main__":
    # player_info: CareerStatsScraper = CareerStatsScraper(player_id="portemi01")
    # data: pd.DataFrame = player_info.get_data()
    # print(data)
    test_scraper_thread(CareerStatsScraper)
