import os
import numpy as np
import pandas as pd

from data_scrape.abstract_base_scraper import AbstractBaseScraper
from sql_app.register.gamelog import Gamelogs


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

    def __init__(self, *, player_id: str, year: int):
        super().__init__(player_id=player_id)

        self.year = year

    @property
    def download_url(self):
        return f"http://www.basketball-reference.com/players/{self.player_initial}/{self.player_id}/gamelog/{self.year}"

    @property
    def save_path(self):
        return os.path.join(
            "player_data", "gamelogs", self.player_initial, self.player_id
        )

    @property
    def save_file(self) -> str:
        return os.path.join(self.full_save_path, f"{self.year}.csv")

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        return list(filter(lambda x: x.shape[1] == 30, datasets))[0]

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # Remove extra column rows from dataset
        data: pd.DataFrame = data[data["Rk"] != "Rk"]

        # Reset the index to all games where player was rostered this season, including Inactive games
        data: pd.DataFrame = data.set_index("Rk")

        return super().clean(data=data)

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data = super().configure_data(data=data)
        data["player_id"] = self.player_id
        return data.fillna(np.nan).replace([np.nan], [None])


if __name__ == "__main__":

    gamelog = GamelogScraper(player_id="jamesle01", year=2024)
    print(gamelog.get_data())
