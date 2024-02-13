# Aliases
import numpy as np
import pandas as pd

# Module imports
import os
import re

# Package imports
from data_scrape.abstract_base_scraper import AbstractBaseScraper
from helpers.string_helpers import convert_season_to_year
from sql_app.register.career_stats import CareerStatss


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

    def __init__(self, *, player_id: str) -> None:
        super().__init__(player_id=player_id)

    @property
    def download_url(self):
        return f"http://www.basketball-reference.com/players/{self.player_initial}/{self.player_id}.html"

    @property
    def save_path(self):
        return os.path.join("player_data", "career_stats", self.player_initial)

    def generate_exception_msg(self, *, exception_type: str) -> str:
        exception_msg = super().generate_exception_msg(exception_type=exception_type)
        return exception_msg + f"{{ id: {self.player_id}}}"

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        # Filter the dataframe to get the career stats dataframe
        season_stat_datasets: list[pd.DataFrame] = list(
            filter(lambda dataset: "Season" in dataset.columns, datasets)
        )
        return season_stat_datasets[0]

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = super().clean(data=data)

        data = data.dropna(subset="Season")
        data = data.dropna(subset="G")

        data["Awards"] = data["Awards"].fillna("")

        return data

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = super().configure_data(data=data)
        data["player_id"] = self.player_id
        data = data.fillna(np.nan).replace([np.nan], [None])
        return data

    def get_active_seasons(self) -> "list[int]":
        try:
            # Filter the career stats to contain just the season averages
            season_stats: pd.DataFrame = self.data[
                self.data["Season"].str.contains("^\d{4}") == True
            ]
            season_stats: pd.DataFrame = season_stats.dropna()

            # Delete duplicate seasons (player played for multiple teams in same season)
            season_stats: pd.DataFrame = season_stats.drop_duplicates(subset="Season")

            # Get the seasons active by converting seasons column to a value list
            seasons_active: list[str] = season_stats["Season"].to_list()
            seasons_active: list[int] = list(
                map(
                    lambda season: convert_season_to_year(season=season), seasons_active
                )
            )
        except Exception as e:
            raise e

        return seasons_active


if __name__ == "__main__":
    player_info: CareerStatsScraper = CareerStatsScraper(player_id="portemi01")
    data: pd.DataFrame = player_info.get_data()
    print(data)
