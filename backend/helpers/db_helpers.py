import pandas as pd
from global_implementations import constants
from helpers.string_helpers import find_closest_match
from sql_app.register.matchup import Matchups
from sql_app.register.gamelog import Gamelogs
from sql_app.register.player_info import PlayerInfos
from sql_app.serializers.player_info import PlayerInfoSerializer
from sql_app.serializers.matchup import MatchupSerializer
from sql_app.serializers.gamelog import GamelogSerializer
from typing import Optional


def get_matchup_gamelog(
    *, id: str, home_player: bool = True
) -> "list[GamelogSerializer]":
    matchup: MatchupSerializer = Matchups.get_record(query={"id": id})

    if not matchup:
        return []

    home_player_df: pd.DataFrame = Gamelogs.filter_records(
        query={"player_id": matchup.home_player_id}, as_df=True
    )
    away_player_df: pd.DataFrame = Gamelogs.filter_records(
        query={"player_id": matchup.away_player_id}, as_df=True
    )

    # Merge the datasets on games they played against each other and drop inactive games
    matchup_gamelog = pd.merge(
        home_player_df,
        away_player_df,
        left_on=["Date", "Tm"],
        right_on=["Date", "Opp"],
    ).dropna()

    # Get the original column names of the datasets that were not duplicated
    column_headers = home_player_df.loc[:, home_player_df.columns != "Date"].columns

    # Create filters to separate the respective datasets for each player
    if home_player:
        subset_filter: list = ["Date"] + list(
            map(lambda stat: f"{stat}_x", column_headers)
        )
    else:
        subset_filter: list = ["Date"] + list(
            map(lambda stat: f"{stat}_y", column_headers)
        )

    rename_function = lambda column: column.rsplit("_", 1)[0]

    # Rename the columns for each player to remove the suffixes
    matchup_data: pd.DataFrame = matchup_gamelog[subset_filter].rename(
        rename_function, axis="columns"
    )

    return [
        GamelogSerializer(**game) for game in matchup_data.to_dict(orient="records")
    ]


def get_player_id(*, player_name: str) -> Optional[str]:
    first_name, last_name = player_name.split(" ")[:2]
    return f"{last_name.lower()[:5]}{first_name.lower()[:2]}01"
    # player: PlayerInfoSerializer = PlayerInfos.get_record(query={"name": player_name})

    # if not player:
    #     player_names: list[str] = PlayerInfos.get_column_values(column="name")

    #     player_name_match: str = find_closest_match(
    #         value=player_name, search_list=player_names
    #     )

    #     if not player_name_match:
    #         return None

    #     player: PlayerInfoSerializer = PlayerInfos.get_record(
    #         query={"name": player_name_match}
    #     )

    # return player.player_id


if __name__ == "__main__":
    get_player_id(player_name="Luka Doncic")
