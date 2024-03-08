import datetime
import logging
import uuid
import numpy as np
import pandas as pd

from typing import Iterable, Unpack, Literal, TypedDict, Optional

from scraper.abstract_base_scraper import AbstractBaseScraper
from exceptions import DBNotFoundException
from sql_app.util.db_helpers import get_player_active_seasons
from sql_app.register.gamelog import Gamelogs
from sql_app.register.matchup import Matchups
from sql_app.register.player import Players
from global_implementations import constants

import time


def convert_minutes_to_float(time: str) -> float:
    if not isinstance(time, str):
        return time

    minutes, seconds = time.split(":")
    result = int(minutes) + round(int(seconds) / 60, ndigits=1)
    return result


def get_days_rest(dataset: pd.DataFrame) -> pd.Series:
    def get_closest_game(date, data: pd.DataFrame) -> Optional[int]:
        # Drop games where the player did not play
        data = data.dropna(subset="G")

        # Get the closest last game the player played in
        date_differences: pd.Series[datetime.timedelta] = (
            date - data[data["Date"] < date]["Date"]
        )

        sorted_dates = date_differences.sort_values()

        if not sorted_dates.empty:
            return sorted_dates[0].days
        else:
            return None

    return dataset["Date"].apply(lambda date: get_closest_game(date, dataset))


def get_result_and_margin(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Split the result column into win/loss and margin of victory.
    """
    result_split = dataset["Unnamed: 7"].str.split(r"\s\(\+*", expand=True, regex=True)
    result_split[1] = result_split[1].str.strip(")")
    dataset["result"] = result_split[0]
    dataset["margin"] = result_split[1]

    return dataset


class QueryDictForm(TypedDict):
    player_last_initial: str
    player_id: str
    year: int


class GamelogScraper(AbstractBaseScraper):
    class Kwargs(TypedDict, total=False):
        identifier_source: Literal["matchups_only", "all"]

    RENAME_COLUMNS = {
        "FT%": "FT_perc",
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "+/-": "plus_minus",
    }
    TRANSFORMATIONS = {
        "MP": lambda x: convert_minutes_to_float(x),
        ("PTS", "id"): lambda x: uuid.uuid4(),
        ("Unnamed: 5", "home"): lambda cell: cell != "@",
    }
    DATA_TRANSFORMATIONS = [get_result_and_margin]
    DATETIME_COLUMNS = {"Date": "%Y-%m-%d"}
    STAT_AUGMENTATIONS = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
        "days_rest": get_days_rest,
    }
    QUERY_SAVE_COLUMNS = ["player_id"]
    COLUMN_ORDERING = ["player_id"]
    QUERY_DICT_FORM = QueryDictForm

    TABLE = Gamelogs
    LOG_LEVEL = logging.WARNING

    def __init__(self, **kwargs: Unpack[Kwargs]):
        super().__init__(**kwargs)

        self.identifier_source: Literal["matchups_only", "all"] = kwargs.get(
            "identifier_source", "matchups_only"
        )

    @property
    def download_url(self):
        return "http://www.basketball-reference.com/players/{player_last_initial}/{player_id}/gamelog/{year}"

    def select_dataset_from_html_tables(
        self, *, datasets: list[pd.DataFrame]
    ) -> pd.DataFrame:
        # TODO: This filter seems awfully presumptuous, maybe we should change it at some point
        return list(filter(lambda x: x.shape[1] == 30, datasets))[0]

    def is_cached(self, *, query: QueryDictForm) -> bool:
        queried_season = query.get("year")
        # TODO: Switch to less than to always update the current season
        if queried_season and queried_season < constants.CURRENT_SEASON:
            gamelogs = Gamelogs.filter_records(
                query={"player_id": query.get("player_id")}, as_df=True
            )

            if gamelogs.empty:
                return False

            start = datetime.datetime(year=queried_season - 1, month=6, day=1)
            end = datetime.datetime(year=queried_season, month=6, day=1)

            gamelogs_from_season = gamelogs[gamelogs["Date"].between(start, end)]
            if not gamelogs_from_season.empty:
                self.logger.info(
                    f"Skipping year {queried_season} for player {query.get('player_id')}. Already saved."
                )
                return True
        return False

    def get_query_set(self) -> Optional[list[QueryDictForm]]:
        # TODO: There has to be a faster way to do this. Without extend and iteration
        # There should simply be a dataset for all active players playing tonight
        player_ids: Iterable[str] = []

        if self.identifier_source == "matchups_only":
            matchups = Matchups.get_all_records(as_df=True)

            home_players = matchups["home_player"].unique()
            away_players = matchups["away_player"].unique()

            if len(home_players) == 0 or len(away_players) == 0:
                raise Exception("No active matchups set.")

            player_ids = np.concatenate(
                (
                    home_players,
                    away_players,
                )
            )

        elif self.identifier_source == "all":
            all_players = Players.get_all_records(as_df=True)

            if not all_players.empty:
                player_ids = list(all_players["id"].values)
            else:
                raise Exception("No player's found in the player info table.")

        query_set: list[QueryDictForm] = []
        for player_id in player_ids:
            if type(player_id) != str:
                self.logger.warning(
                    f"Could not get query for player with id {player_id}. 'player_id' not a string."
                )
                continue

            try:
                active_seasons = get_player_active_seasons(player_id=player_id)

                queries: list[QueryDictForm] = [
                    {
                        "player_last_initial": player_id[0],
                        "player_id": player_id,
                        "year": year,
                    }
                    for year in active_seasons
                ]

                query_set.extend(queries)

            except DBNotFoundException:
                self.logger.warning(
                    f"Could not find active seasons for player with id {player_id}."
                )
                continue

        return query_set

    def clean(self, *, data: pd.DataFrame) -> pd.DataFrame:
        # TODO: We can create class attributes for removing rows and setting the index
        # Remove extra column rows from dataset
        data = data[data["Rk"] != "Rk"]

        # Reset the index to all games where player was rostered this season, including Inactive games
        data = data.set_index("Rk")

        return super().clean(data=data)


if __name__ == "__main__":

    gamelog = GamelogScraper(identifier_source="matchups_only")
    gamelog.get_data(
        query={"player_last_initial": "j", "player_id": "jamesle01", "year": 2024}
    )
