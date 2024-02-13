import pandas as pd
import re

from data_scrape.abstract_base_scraper import AbstractBaseScraper
from helpers.db_helpers import get_player_id
from sql_app.register.player_prop import PlayerProps
from typing import Callable
import threading

import time

plus_minus_match = re.compile("−|\+")
minus_match = re.compile("−")
plus_match = re.compile("\+")

line_split_match = re.compile("^[^\d]*")


def get_player_props(*, dataset: pd.DataFrame):

    def split_line_column_by_regex(column, regex):
        data = pd.DataFrame = dataset[column].str.split(regex, expand=True)
        data = data.dropna(subset=1)

        # favored_over_data[0] = favored_over_data[0].astype(str)
        data[0] = data[0].str.split(line_split_match, expand=True)[1]

        # Set column types
        data[0] = data[0].astype(float)
        data[1] = data[1].astype(int)

        return data

    def split_line_column_into_dataframe(column: str) -> pd.DataFrame:

        unfavored_prop_data = split_line_column_by_regex(
            column=column, regex=plus_match
        )
        favored_prop_data = split_line_column_by_regex(column=column, regex=minus_match)

        unfavored_prop_data["implied_odds"] = round(
            100 / (unfavored_prop_data[1] + 100) * 100, ndigits=2
        )
        favored_prop_data["implied_odds"] = round(
            favored_prop_data[1] / (favored_prop_data[1] + 100) * 100, ndigits=2
        )

        favored_prop_data[1] = -favored_prop_data[1]

        full_data = pd.concat([unfavored_prop_data, favored_prop_data]).sort_index()

        full_data = full_data.rename(columns={0: "line", 1: "odds"})
        full_data.index.set_names(["id"], inplace=True)

        return full_data

    over_data = split_line_column_into_dataframe("OVER")
    under_data = split_line_column_into_dataframe("UNDER")

    over_under_odds = pd.merge(
        over_data,
        under_data,
        on=["id", "line"],
        suffixes=["_over", "_under"],
    )

    full_data = pd.merge(
        dataset,
        over_under_odds,
        left_index=True,
        right_index=True,
    )

    return full_data.drop(columns=["OVER", "UNDER"])


def set_player_id(*, dataset: pd.DataFrame) -> pd.DataFrame:
    dataset["player_id"] = dataset["player_name"].map(
        lambda name: get_player_id(player_name=name)
    )
    return dataset


class PlayerPropsScraper(AbstractBaseScraper, threading.Thread):
    _DEFAULT_ERROR_MSG: str = "There was an error."
    _exception_msgs: "dict[str: str]" = {
        "load_data": _DEFAULT_ERROR_MSG,
        "download_data": _DEFAULT_ERROR_MSG,
    }

    COLUMN_TYPES: "dict[str: str]" = {}
    DATETIME_COLUMNS: "dict[str: str]" = {}
    FILTERS: "list[Callable]" = []
    RENAME_COLUMNS: "dict[str:str]" = {"PLAYER": "player_name"}
    TABLE = PlayerProps
    DROP_COLUMNS: "list[str]" = []
    TRANSFORMATIONS = {}
    DATA_TRANSFORMATIONS = [get_player_props, set_player_id]

    def __init__(self, *, stat: str):
        self.stat = stat
        threading.Thread.__init__()
        self.RUNNING = False

    @property
    def download_url(self):
        return f"http://sportsbook.draftkings.com/nba-player-props?category=player-{self.stat}&subcategory={self.stat}"

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        return pd.concat(datasets, ignore_index=True)

    def configure_data(self, *, data: pd.DataFrame) -> pd.DataFrame:
        data["stat"] = self.stat
        return super().configure_data(data=data)

    def run(self) -> None:
        self.RUNNING = True
        stats = ["points", "assists", "threes", "rebounds"]
        stat_idx = 0
        while self.RUNNING:
            self.stat = stats[stat_idx]
            self.get_data()

            time.sleep(1)


if __name__ == "__main__":
    # player_props = get_player_props()
    player_props_scraper = PlayerPropsScraper(stat="assists")
    player_props_scraper.get_data()
    # check = re.split(line_split_match, "O 3.5")
    # print(check)
