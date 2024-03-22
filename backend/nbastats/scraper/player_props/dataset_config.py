import logging
import re
import uuid
from datetime import datetime

import pandas as pd
from base.scraper import BaseHTMLDatasetConfig, TableConfig
from base.sql_app.register import AdvancedQuery
from nbastats.sql_app.register import Games, PlayerProps, Players
from nbastats.sql_app.serializers import ReadPlayerSerializer
from nbastats.sql_app.util.db_helpers import get_player_id

plus_minus_match = re.compile(r"−|\+")
minus_match = re.compile(r"−")
plus_match = re.compile(r"\+")

line_split_match = r"^[^\d]*"

logger = logging.getLogger("main")


def get_player_props(dataset: pd.DataFrame) -> pd.DataFrame:
    def split_line_column_by_regex(column, regex):
        data: pd.DataFrame = dataset[column].str.split(regex, expand=True)
        data: pd.DataFrame = data.dropna(subset=1)

        # favored_over_data[0] = favored_over_data[0].astype(str)
        data[0] = data[0].str.split(line_split_match, expand=True, regex=True)[1]

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
    full_data: pd.DataFrame = full_data.rename(
        columns={
            "odds_over": "over",
            "odds_under": "under",
            "implied_odds_over": "over_implied",
            "implied_odds_under": "under_implied",
        }
    )
    return full_data


def get_game_id(*, player_id: str):
    player: ReadPlayerSerializer = Players.get_record(query={"id": player_id})  # type: ignore
    todays_games: pd.DataFrame = Games.filter_by_datetime(
        min_datetime=datetime.today(), as_df=True
    )

    cur_team_game = todays_games[
        (todays_games["home"] == getattr(player.team, "id", None))
        | (todays_games["away"] == getattr(player.team, "id", None))
    ]

    if not cur_team_game.empty:
        cur_team_game = cur_team_game.iloc[0, :]
        return cur_team_game["id"]
    else:
        return None


def set_statuses(dataset: pd.DataFrame) -> pd.DataFrame:
    todays_games = Games.filter_by_datetime(min_datetime=datetime.today(), as_df=True)

    todays_game_ids = list(todays_games["id"].values)

    todays_props = PlayerProps.filter_records_advanced(
        query=AdvancedQuery(in_={"game_id": todays_game_ids})
    )

    dataset = dataset[dataset["player_id"] != "harteis01"]

    if todays_props.empty:
        dataset["status"] = 1
    else:
        merged = todays_props.merge(
            dataset,
            how="left",
            left_on=["game", "player", "stat"],
            right_on=["game_id", "player_id", "stat"],
        )

        print(merged.columns)

        locked_lines = merged[merged["id_y"].isna()]["id_x"].values

        print(locked_lines)

    return dataset


class PlayerPropsTableConfig(TableConfig):

    RENAME_COLUMNS = {
        "PLAYER": "name",
    }
    RENAME_VALUES = {
        "stat": {
            "points": "PTS",
            "assists": "AST",
            "threes": "THP",
            "rebounds": "TRB",
            "pts-+-reb-+-ast": "PRA",
            "pts-+-reb": "PR",
            "pts-+-ast": "PA",
            "ast-+-reb": "RA",
        }
    }
    TRANSFORMATIONS = {
        ("name", "player_id"): lambda name: get_player_id(player_name=name),
        ("name", "id"): lambda x: uuid.uuid4(),
        ("player_id", "game_id"): lambda player_id: get_game_id(player_id=player_id),
    }
    DATA_TRANSFORMATIONS = [get_player_props, set_statuses]
    QUERY_SAVE_COLUMNS = {"stat": "stat_subcategory"}
    REQUIRED_COLUMNS = ["player_id"]

    def __init__(self, **kwargs):
        super().__init__(
            identification_function=identification_function,
            sql_table=PlayerProps,
            **kwargs,
        )


class PlayerPropsDatasetConfig(BaseHTMLDatasetConfig):

    def __init__(self, **kwargs):
        kwargs.setdefault("name", "PlayerPropsDataset")
        super().__init__(
            default_query_set=[
                {"stat_category": "points", "stat_subcategory": "points"},
                {"stat_category": "assists", "stat_subcategory": "assists"},
                {"stat_category": "threes", "stat_subcategory": "threes"},
                {"stat_category": "rebounds", "stat_subcategory": "rebounds"},
                {"stat_category": "combos", "stat_subcategory": "pts-+-reb-+-ast"},
                {"stat_category": "combos", "stat_subcategory": "pts-+-reb"},
                {"stat_category": "combos", "stat_subcategory": "pts-+-ast"},
                {"stat_category": "combos", "stat_subcategory": "ast-+-reb"},
            ],
            **kwargs,
        )

    @property
    def base_download_url(self):
        return "http://sportsbook.draftkings.com/nba-player-props?category=player-{stat_category}&subcategory={stat_subcategory}"
