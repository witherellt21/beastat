import datetime
import re
import uuid
from typing import Optional

import pandas as pd
from core.scraper.base.util import QueryArgs
from nbastats.global_implementations import constants
from nbastats.scrapers.util.team_helpers import get_team_id_by_abbr
from nbastats.sql_app.models import Game, Gamelog
from nbastats.sql_app.register import Games, PlayerBoxScores
from nbastats.sql_app.serializers import ReadGameSerializer
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
        print(time)
        print(time.split(":"))
        raise e


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
            print(data)
            print(date_differences)
            print(sorted_dates)
            raise e

    return dataset["Date"].apply(lambda date: get_closest_game(date, dataset))


def get_game_id(row: pd.Series) -> str:

    home_team = row["Tm"] if row["home"] else row["Opp"]
    away_team = row["Opp"] if row["home"] else row["Tm"]

    home_team_id = get_team_id_by_abbr(home_team)
    away_team_id = get_team_id_by_abbr(away_team)

    game: ReadGameSerializer = Games.update_or_insert_record(
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

        foreign_keys = PlayerBoxScores.get_foreign_relationships()

        foreign_keys_remap = {
            foreign_key: f"{foreign_key}_id" for foreign_key in foreign_keys
        }

        gamelogs_from_season = gamelogs_from_season.rename(columns=foreign_keys_remap)

        return gamelogs_from_season

    return pd.DataFrame()
