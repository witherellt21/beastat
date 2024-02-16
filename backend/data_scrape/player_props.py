import pandas as pd
import re

from data_scrape.abstract_base_scraper import AbstractBaseScraper
from helpers.db_helpers import get_player_id
from sql_app.register.player_prop import PlayerProps
from sql_app.register.player_prop import PropLines
from sql_app.serializers.player_prop import PlayerPropSerializer
from typing import Callable
import threading
import traceback
import logging
import time

from pydantic_core import ValidationError

plus_minus_match = re.compile("−|\+")
minus_match = re.compile("−")
plus_match = re.compile("\+")

line_split_match = re.compile("^[^\d]*")


def get_player_props(*, dataset: pd.DataFrame):
    def split_line_column_by_regex(column, regex):
        data: pd.DataFrame = dataset[column].str.split(regex, expand=True)
        data: pd.DataFrame = data.dropna(subset=1)

        # favored_over_data[0] = favored_over_data[0].astype(str)
        data[0] = data[0].str.split(line_split_match, expand=True)[1]

        # Set column types
        data[0] = data[0].astype(float)
        data[1] = data[1].astype(int)

        return data

    def split_line_column_into_dataframe(column: str) -> pd.DataFrame:
        # Get the lines and odds data
        # The unfavored and favored data have to be separated and recombine as they have different behavior.
        unfavored_prop_data: pd.DataFrame = split_line_column_by_regex(
            column=column, regex=plus_match
        )
        favored_prop_data: pd.DataFrame = split_line_column_by_regex(
            column=column, regex=minus_match
        )

        # Set the "implied_odds" based on the betting odds
        unfavored_prop_data["implied_odds"] = (
            100 / (unfavored_prop_data[1] + 100) * 100
        ).round(2)

        favored_prop_data["implied_odds"] = (
            favored_prop_data[1] / (favored_prop_data[1] + 100) * 100
        ).round(2)

        # Invert the value for favored lines
        favored_prop_data[1] = -favored_prop_data[1]

        # Pull the favored and unfavored datasets back together
        full_data: pd.DataFrame = pd.concat(
            [unfavored_prop_data, favored_prop_data]
        ).sort_index()

        # Rename the columns for the dataset
        full_data: pd.DataFrame = full_data.rename(columns={0: "line", 1: "odds"})
        full_data.index = full_data.index.set_names(["id"])

        return full_data

    # Copy the input data in case we have a failure
    input_data = dataset.copy()

    # Split our over/under data to extrapolate the line/odds for each
    try:
        over_data = split_line_column_into_dataframe("OVER")
        under_data = split_line_column_into_dataframe("UNDER")
    except Exception as e:
        raise Exception(
            f"Error getting player props data: {e}. Original dataset: \n {input_data}"
        )

    # Merge the new over/under data to a single dataset
    over_under_odds = pd.merge(
        over_data,
        under_data,
        on=["id", "line"],
        suffixes=["_over", "_under"],
    )

    # Add the new over/under data to our initial dataset
    full_data = pd.merge(
        dataset,
        over_under_odds,
        left_index=True,
        right_index=True,
    )

    # Drop the old over/under data and return
    full_data = full_data.drop(columns=["OVER", "UNDER"])
    return full_data


def set_player_id(*, dataset: pd.DataFrame) -> pd.DataFrame:
    dataset["player_id"] = dataset["player_name"].map(
        lambda name: get_player_id(player_name=name)
    )
    return dataset


class PlayerPropsScraper(AbstractBaseScraper):
    RENAME_COLUMNS: "dict[str:str]" = {"PLAYER": "player_name"}
    REPLACE_VALUES = {
        "points": "PTS",
        "assists": "AST",
        "threes": "THP",
        "rebounds": "TRB",
    }
    DATA_TRANSFORMATIONS = [get_player_props, set_player_id]

    DEFAULT_IDENTIFIERS: "dict[str:list]" = ["points", "assists", "threes", "rebounds"]
    SAVE_IDENTIFIER_AS: str = "stat"

    TABLE = PlayerProps
    REFRESH_RATE = 1

    LOG_LEVEL = logging.WARNING

    @property
    def download_url(self):
        return "http://sportsbook.draftkings.com/nba-player-props?category=player-{}&subcategory={}"

    def format_url_args(self, identifier):
        return [identifier, identifier]

    def select_dataset_from_html_tables(
        self, *, datasets: "list[pd.DataFrame]"
    ) -> pd.DataFrame:
        return pd.concat(datasets, ignore_index=True)

    def cache_data(self, *, data: pd.DataFrame) -> None:
        """
        - Get or create the player props instance
        - Create or update the prop line on the player instance
        """
        self.logger.debug("Saving data to database.")

        row_dicts = data.to_dict(orient="records")
        for row in row_dicts:

            if row["player_id"] == None:
                self.logger.debug(
                    f"Player's ID does not exist: player_name = {row.get('player_name')}. Congifure the player info scraper to get all active player's id's."
                )
                continue

            player: PlayerPropSerializer = PlayerProps.get_or_create(
                data={"player_id": row["player_id"], "name": row["player_name"]}
            )

            prop_line = PropLines.update_or_insert_record(
                data={
                    "player_id": player.id,
                    "stat": row["stat"],
                    "line": row["line"],
                    "over": row["odds_over"],
                    "under": row["odds_under"],
                    "over_implied": row["implied_odds_over"],
                    "under_implied": row["implied_odds_under"],
                }
            )

        self.logger.debug(f"\n{data}")


def test_scraper_thread():
    player_props_scraper = PlayerPropsScraper()
    player_props_scraper.start()

    start = time.time()
    while time.time() - start < 10:
        time.sleep(1)

    player_props_scraper.RUNNING = False


if __name__ == "__main__":
    # player_props = get_player_props()
    # player_props_scraper = PlayerPropsScraper()
    # player_props_scraper.get_data(identifier="assists")
    # check = re.split(line_split_match, "O 3.5")
    # print(check)
    test_scraper_thread()
