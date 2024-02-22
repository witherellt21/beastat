import logging
import numpy as np
import pandas as pd

from typing import Iterable, Unpack, Literal, TypedDict

from data_scrape.abstract_base_scraper import AbstractBaseScraper, ScraperKwargs
from exceptions import NoDataFoundException
from helpers.db_helpers import get_player_active_seasons
from sql_app.register.gamelog import Gamelogs
from sql_app.register.matchup import Matchups
from sql_app.register.player_info import PlayerInfos


def convert_minutes_to_float(time: str) -> float:
    if not isinstance(time, str):
        return time

    minutes, seconds = time.split(":")
    result = int(minutes) + round(int(seconds) / 60, ndigits=1)
    return result


class GamelogScraper(AbstractBaseScraper):
    class Kwargs(TypedDict, total=False):
        identifier_source: Literal["matchups_only", "all"]

    RENAME_COLUMNS = {
        "Unnamed: 7": "streak",
        "FT%": "FT_perc",
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "+/-": "plus_minus",
    }
    TRANSFORMATIONS = {"MP": lambda x: convert_minutes_to_float(x)}
    DATETIME_COLUMNS = {"Date": "%Y-%m-%d"}
    STAT_AUGMENTATIONS = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
    }
    QUERY_SAVE_COLUMNS = ["player_id"]
    COLUMN_ORDERING = ["player_id"]

    TABLE = Gamelogs
    LOG_LEVEL = logging.DEBUG

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

    def get_query_set(self) -> list[dict[str, str]]:
        # TODO: There has to be a faster way to do this. Without extend and iteration
        # There should simply be a dataset for all active players playing tonight
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

        query_set: list[dict[str, str]] = []
        for player_id in player_ids:
            try:
                active_seasons = get_player_active_seasons(player_id=player_id)

                query_set.extend(
                    [
                        {
                            "player_last_initial": player_id[0],
                            "player_id": player_id,
                            "year": str(year),
                        }
                        for year in active_seasons
                    ]
                )

            except NoDataFoundException:
                self.logger.error(
                    f"Could not find active seasons for player with id {player_id}."
                )
                continue

        self.logger.debug(f"Getting gamelogs for {query_set}")

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
        query={"player_last_initial": "j", "player_id": "jamesle01", "year": "2023"}
    )
