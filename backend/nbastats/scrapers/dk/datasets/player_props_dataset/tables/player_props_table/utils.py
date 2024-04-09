import re
import uuid
from datetime import datetime

import pandas as pd
from core.scraper import (
    AugmentationField,
    BaseHTMLTableSerializer,
    CharField,
    QueryArgField,
    RenameField,
    TransformationField,
)
from core.sql_app import AdvancedQuery
from nbastats.sql_app.register import BasicInfo, Games, PlayerProps
from nbastats.sql_app.serializers import ReadPlayerSerializer

plus_minus_match = re.compile(r"−|\+")
minus_match = re.compile(r"−")
plus_match = re.compile(r"\+")
line_split_match = r"^[^\d]*"


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
        print("DATASET\n", dataset)
        over_data = split_line_column_into_dataframe("OVER")
        under_data = split_line_column_into_dataframe("UNDER")
    except Exception as e:
        raise Exception(
            f"Error getting player props data: {e}. Original dataset: \n {input_data}"
        )

    # Merge the new over/under data to a single dataset
    full_data = pd.merge(
        over_data,
        under_data,
        on=["id", "line"],
        suffixes=["_over", "_under"],
    )

    # Drop the old over/under data and return
    full_data: pd.DataFrame = full_data.rename(
        columns={
            "odds_over": "over",
            "odds_under": "under",
            "implied_odds_over": "over_implied",
            "implied_odds_under": "under_implied",
        }
    )
    return full_data


def get_game_id(player_id: str):
    player: ReadPlayerSerializer = BasicInfo.get_record(query={"id": player_id})  # type: ignore
    todays_games: pd.DataFrame = Games.filter_by_datetime(
        min_datetime=datetime.today(), as_df=True
    )

    if todays_games.empty:
        return None

    cur_team_game = todays_games[
        (todays_games["home"] == getattr(player.team, "id", None))
        | (todays_games["away"] == getattr(player.team, "id", None))
    ]

    if not cur_team_game.empty:
        cur_team_game = cur_team_game.iloc[0, :]
        return cur_team_game["id"]
    else:
        return None


def set_statuses(dataset: pd.DataFrame) -> pd.Series:
    todays_games = Games.filter_by_datetime(min_datetime=datetime.today(), as_df=True)

    if todays_games.empty:
        return pd.Series(data={"status": 0 for i in range(PlayerProps.count_records())})

    todays_game_ids = list(todays_games["id"].values)

    todays_props = PlayerProps.filter_records_advanced(
        query=AdvancedQuery(in_={"game_id": todays_game_ids})
    )

    if todays_props.empty:
        dataset["status"] = 1
    else:
        dataset["status"] = 1
        merged = todays_props.merge(
            dataset,
            how="left",
            left_on=["game", "player", "stat"],
            right_on=["game_id", "player_id", "stat"],
        )

        locked_lines = merged[merged["id_y"].isna()]["id_x"].values

    return dataset["status"]


class PlayerPropsTableEntrySerializer(BaseHTMLTableSerializer):
    id = CharField(default=uuid.uuid4)
    player_name = RenameField("PLAYER", type=str, cache=False)
    player_id = TransformationField(
        str, BasicInfo.get_player_id_from_name, from_columns=["player_name"]
    )
    game_id = TransformationField(
        str, get_game_id, from_columns=["player_id"], null=False
    )
    status = AugmentationField(int, set_statuses, null=True)
    stat = QueryArgField(
        from_column="stat_subcategory",
        replace_values={
            "points": "PTS",
            "assists": "AST",
            "threes": "THP",
            "rebounds": "TRB",
            "pts-+-reb-+-ast": "PRA",
            "pts-+-reb": "PR",
            "pts-+-ast": "PA",
            "ast-+-reb": "RA",
        },
    )
    odds = AugmentationField(
        float,
        get_player_props,
        to_columns=["line", "over", "over_implied", "under", "under_implied"],
    )
