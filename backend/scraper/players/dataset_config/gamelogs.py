import datetime
import uuid
from typing import Optional

import numpy as np
import pandas as pd
from global_implementations import constants
from playhouse.shortcuts import model_to_dict
from pydantic import UUID4
from scraper.base import BaseHTMLDatasetConfig, QueryArgs, TableConfig
from sql_app.models import Game, Gamelog
from sql_app.register import Gamelogs, Games
from sql_app.serializers import ReadGameSerializer

from .career_stats import get_team_id_by_abbr


def convert_minutes_to_float(time: str) -> float:
    if not isinstance(time, str):
        return time

    minutes, seconds = time.split(":")
    result = int(minutes) + round(int(seconds) / 60, ndigits=1)
    return result


def get_result_and_margin(dataset: pd.DataFrame) -> pd.DataFrame:
    """
    Split the result column into win/loss and margin of victory.
    """
    result_split = dataset["Unnamed: 7"].str.split(r"\s\(\+*", expand=True, regex=True)
    result_split[1] = result_split[1].str.strip(")")
    dataset["result"] = result_split[0]
    dataset["margin"] = result_split[1]

    return dataset


def get_days_rest(dataset: pd.DataFrame) -> pd.Series:
    def get_closest_game(date, data: pd.DataFrame) -> Optional[int]:
        # Drop games where the player did not play
        data = data.dropna(subset="G")

        # Get the closest last game the player played in
        date_differences: pd.Series[datetime.timedelta] = (
            date - data[data["Date"] < date]["Date"]
        )

        sorted_dates: pd.Series[datetime.timedelta] = date_differences.sort_values()

        try:

            if not sorted_dates.empty:
                return sorted_dates.iloc[0].days
            else:
                return None
        except Exception as e:
            print(data)
            print(date_differences)
            print(sorted_dates)
            raise e

    return dataset["Date"].apply(lambda date: get_closest_game(date, dataset))


def get_game_ids(dataset: pd.DataFrame) -> pd.Series:
    def get_game_id(
        date: datetime.datetime, team: str, opponent: str, home: bool
    ) -> UUID4:
        home_team = team if home else opponent
        away_team = opponent if home else team

        home_team_id = get_team_id_by_abbr(home_team)
        away_team_id = get_team_id_by_abbr(away_team)

        game: ReadGameSerializer = Games.update_or_insert_record(
            data={"date_time": date, "home_id": home_team_id, "away_id": away_team_id}
        )  # type: ignore

        return game.id

    game_id = dataset.apply(
        lambda row: get_game_id(
            row["Date"], row["Tm"], row["Opp"], row["home"]
        ),  # type: ignore
        axis=1,
    )  # type: ignore

    return game_id


class GamelogTableConfig(TableConfig):
    """
    Here we will include the cleaning function stuff as class attributes
    """

    RENAME_COLUMNS = {
        "FT%": "FT_perc",
        "FG%": "FG_perc",
        "3P": "THP",
        "3PA": "THPA",
        "3P%": "THP_perc",
        "+/-": "plus_minus",
    }
    RENAME_VALUES = {
        "Rk": {"Rk": np.nan},
        "G": {"": np.nan},
        "TWP_perc": {"": np.nan},
        "THP_perc": {"": np.nan},
        "FT_perc": {"": np.nan},
        "FG_perc": {"": np.nan},
    }
    REQUIRED_FIELDS = ["Rk"]

    TRANSFORMATIONS = {
        "MP": lambda x: convert_minutes_to_float(x),
        ("PTS", "id"): lambda x: uuid.uuid4(),
        ("Unnamed: 5", "home"): lambda cell: cell != "@",
    }
    DATA_TRANSFORMATIONS = [
        get_result_and_margin,
    ]
    DATETIME_COLUMNS = {"Date": "%Y-%m-%d"}
    STAT_AUGMENTATIONS = {
        "PA": "PTS+AST",
        "PR": "PTS+TRB",
        "RA": "TRB+AST",
        "PRA": "PTS+TRB+AST",
        "days_rest": get_days_rest,
        "game_id": get_game_ids,
    }
    QUERY_SAVE_COLUMNS = {"player_id": "player_id"}
    COLUMN_ORDERING = ["player_id"]

    # LOG_LEVEL = logging.WARNING

    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Gamelogs")

        super().__init__(
            identification_function=lambda dataset: len(dataset.columns) == 30,
            sql_table=Gamelogs,
            **kwargs,
        )

    def cached_data(self, *, query_args: Optional[QueryArgs] = None) -> pd.DataFrame:
        if query_args == None:
            return super().cached_data(query_args=query_args)

        queried_season = query_args.get("year", None)
        # TODO: Switch to less than to always update the current season
        if queried_season and int(queried_season) <= constants.CURRENT_SEASON:
            start = datetime.datetime(year=queried_season - 1, month=6, day=1)
            end = datetime.datetime(year=queried_season, month=6, day=1)

            search = (
                Gamelog.select()
                .join(Game, on=Game.id == Gamelog.game)
                .where(
                    Gamelog.player == query_args.get("player_id"),
                    Game.date_time > start,
                    Game.date_time < end,
                )
            )

            rows = []
            for row in search:
                rows.append(model_to_dict(row, recurse=False))

            gamelogs_from_season = pd.DataFrame(rows)

            foreign_keys = Gamelogs.get_foreign_relationships()

            foreign_keys_remap = {
                foreign_key: f"{foreign_key}_id" for foreign_key in foreign_keys
            }

            gamelogs_from_season = gamelogs_from_season.rename(
                columns=foreign_keys_remap
            )

            return gamelogs_from_season

        return super().cached_data(query_args=query_args)


class GamelogDatasetConfig(BaseHTMLDatasetConfig):
    # LOG_LEVEL = logging.WARNING

    def __init__(self, **kwargs):
        kwargs.setdefault("name", "Gamelogs")

        super().__init__(**kwargs)

    @property
    def base_download_url(self):
        return "http://www.basketball-reference.com/players/{player_last_initial}/{player_id}/gamelog/{year}"
