import datetime
import re
import uuid
from typing import Optional

import numpy as np
import pandas as pd
from core.scraper import (
    AugmentationField,
    BaseHTMLTableSerializer,
    CharField,
    DatetimeField,
    FloatField,
    QueryArgField,
    QueryArgs,
    RenameField,
    TransformationField,
)
from lib.util import sum_nullables
from nbastats import constants
from nbastats.db.register import Games, PlayerBoxScores, Teams
from nbastats.db.register.models import Game, Gamelog
from nbastats.db.register.serializers import GameReadSerializer
from pandera.typing import Series
from playhouse.shortcuts import model_to_dict
from pydantic import UUID4


def convert_minutes_to_float(time: str) -> float:
    if not isinstance(time, str):
        return time

    try:
        minutes, seconds = time.split(":")
        result = int(minutes) + round(int(seconds) / 60, ndigits=1)
        return result
    except Exception as e:
        raise Exception(
            f"Error converting minutes to float: {e}. Args: time:{type(time)}={time}"
        )


def get_result_and_margin(result: str) -> Series[str]:
    """
    Split the result column into win/loss and margin of victory.
    """
    result_split: list[str] = re.split(r"\s\(\+*", result)
    result_split[1] = result_split[1].strip(")")

    return pd.Series([result_split[0], result_split[1]])  # type: ignore


def get_closest_games(data: pd.DataFrame) -> pd.Series:
    # # Drop games where the player did not play
    data = data.dropna(subset="G")
    data = data.sort_values("Date")

    days_rest = data["Date"].diff().apply(lambda diff: diff.days)
    return days_rest


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
            raise e

    return dataset["Date"].apply(lambda date: get_closest_game(date, dataset))


def get_game_id(row: pd.Series) -> UUID4:

    home_team = row["Tm"] if row["home"] else row["Opp"]
    away_team = row["Opp"] if row["home"] else row["Tm"]

    home_team_id = Teams.get_team_id_or_nan(home_team, raise_exception=True)
    away_team_id = Teams.get_team_id_or_nan(away_team, raise_exception=True)

    game: GameReadSerializer = Games.update_or_insert_record(
        data={
            "id": uuid.uuid4(),
            "date_time": row["Date"],
            "home_id": home_team_id,
            "away_id": away_team_id,
        }
    )  # type: ignore

    return game.id


def has_30_columns(tables: list[pd.DataFrame]) -> Optional[pd.DataFrame]:
    data = next(
        (table for table in tables if len(table.columns) == 30),
        None,
    )
    return data


def get_cached_gamelog_query_data(query_args: QueryArgs):
    queried_season = query_args.get("year", None)
    # TODO: Switch to less than to always update the current season
    if queried_season and int(queried_season) <= constants.CURRENT_SEASON:
        start = datetime.datetime(year=int(queried_season) - 1, month=6, day=1)
        end = datetime.datetime(year=int(queried_season), month=6, day=1)

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

        foreign_keys = PlayerBoxScores.get_foreign_relationships()

        foreign_keys_remap = {
            foreign_key: f"{foreign_key}_id" for foreign_key in foreign_keys
        }

        gamelogs_from_season = gamelogs_from_season.rename(columns=foreign_keys_remap)

        return gamelogs_from_season

    return pd.DataFrame()


class PlayerBoxScoreTableConfig(BaseHTMLTableSerializer):
    Rk = CharField(replace_values={"Rk": np.nan}, cache=False)
    id = CharField(default=uuid.uuid4)
    player_id = QueryArgField("player_id")
    G = CharField(replace_values={"": np.nan}, null=True)
    Date = DatetimeField(format="%Y-%m-%d", null=True)
    Age = CharField()
    home = TransformationField(
        str, lambda cell: cell != "@", from_columns=["Unnamed: 5"], null=True
    )
    game_id = TransformationField(
        str,
        get_game_id,
        from_columns=["Date", "Tm", "Opp", "home"],
        to_columns=["game_id"],
        null=True,
    )
    GS = CharField(null=True)
    MP = TransformationField(float, convert_minutes_to_float, null=True)
    FG = FloatField(null=True)
    FGA = FloatField(null=True)
    FG_perc = RenameField("FG%", type=float, null=True, replace_values={"": np.nan})
    THP = RenameField("3P", type=float, null=True)
    THPA = RenameField("3PA", type=float, null=True)
    THP_perc = RenameField("3P%", type=float, null=True, replace_values={"": np.nan})
    FT = FloatField(null=True)
    FTA = FloatField(null=True)
    FT_perc = RenameField("FT%", type=float, null=True, replace_values={"": np.nan})
    result = TransformationField(
        str,
        get_result_and_margin,
        from_columns=["Unnamed: 7"],
        to_columns=["result", "margin"],
    )
    ORB = FloatField(null=True)
    DRB = FloatField(null=True)
    TRB = FloatField(null=True)
    AST = FloatField(null=True)
    STL = FloatField(null=True)
    BLK = FloatField(null=True)
    TOV = FloatField(null=True)
    PF = FloatField(null=True)
    PTS = FloatField(null=True)
    GmSc = FloatField(null=True)
    plus_minus = RenameField("+/-", type=float, null=True)
    PA = TransformationField(
        float,
        lambda row: sum_nullables(row["PTS"], row["AST"]),
        null=True,
        from_columns=["PTS", "AST"],
    )
    PR = TransformationField(
        float,
        lambda row: sum_nullables(row["PTS"], row["TRB"]),
        null=True,
        from_columns=["PTS", "TRB"],
    )
    RA = TransformationField(
        float,
        lambda row: sum_nullables(row["TRB"], row["AST"]),
        null=True,
        from_columns=["TRB", "AST"],
    )
    PRA = TransformationField(
        float,
        lambda row: sum_nullables(row["PTS"], row["TRB"], row["AST"]),
        null=True,
        from_columns=["PTS", "TRB", "AST"],
    )
    days_rest = AugmentationField(
        float,
        get_closest_games,
        null=True,
    )
