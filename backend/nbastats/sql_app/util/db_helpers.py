import logging
from typing import Literal, Optional

import pandas as pd
from exceptions import DBNotFoundException
from lib.dataframes import filter_with_bounds
from nbastats.sql_app.register import BasicInfo, Matchups, PlayerBoxScores
from nbastats.sql_app.register.serializers import (
    GamelogSerializer,
    MatchupReadSerializer,
)
from pydantic import BaseModel

logger = logging.getLogger("main")


def get_matchup_gamelog(
    *, id: str, home_player: bool = True
) -> "list[GamelogSerializer]":
    matchup = Matchups.get_record(query={"id": id})

    if not matchup:
        return []

    home_player_df: pd.DataFrame = PlayerBoxScores.filter_records(
        query={"player_id": matchup.home_player_id}, as_df=True  # type: ignore
    )
    away_player_df: pd.DataFrame = PlayerBoxScores.filter_records(
        query={"player_id": matchup.away_player_id}, as_df=True  # type: ignore
    )

    if home_player_df.empty or away_player_df.empty:
        return []

    # Merge the datasets on games they played against each other and drop inactive games
    matchup_gamelog = pd.merge(
        home_player_df,
        away_player_df,
        left_on=["Date", "Tm"],
        right_on=["Date", "Opp"],
    ).dropna()

    # Get the original column names of the datasets that were not duplicated
    # column_headers = home_player_df.loc[:, home_player_df.columns != "Date"].columns
    all_column_headers = home_player_df.columns.to_list()
    column_headers = all_column_headers.pop(all_column_headers.index("Date"))

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

    # records = matchup_data.to_dict(orient="records")

    return [
        GamelogSerializer(**game.__dict__)
        for game in matchup_data.to_dict(orient="records")
    ]


class BoundedQuery(BaseModel):
    min: Optional[int] = None
    max: Optional[int] = None
    # bounding:


class GamelogFilter(BaseModel):
    # query: Optional[str] = None
    minutes_played: BoundedQuery = BoundedQuery()
    limit: int
    margin: BoundedQuery = BoundedQuery()
    gameLocation: Optional[Literal["home", "away"]] = None
    inStartingLineup: Optional[Literal[1, 0]] = None
    matchups_only: bool = False
    date: BoundedQuery = BoundedQuery()
    daysRest: BoundedQuery = BoundedQuery()
    withoutTeammates: list[str] = []
    withTeammates: list[str] = []


def filter_gamelog(*, player_id: str, query: GamelogFilter) -> pd.DataFrame:
    if query.matchups_only:
        gamelog: pd.DataFrame = get_matchup_gamelog_by_player_id(player_id=player_id)
    else:
        gamelog: pd.DataFrame = PlayerBoxScores.filter_records(
            query={"player_id": player_id}, as_df=True
        )

    if gamelog.empty:
        return gamelog

    gamelog = gamelog.dropna(subset=["G"])

    # average_minutes_played = career_gamelog["MP"].mean()

    # career_gamelog = career_gamelog[
    #     career_gamelog["MP"] >= average_minutes_played * 0.9
    # ]
    # if query:
    #     print(query)
    #     gamelog: pd.DataFrame = gamelog.query(query.query)
    # print(gamelog["days_rest"].astype(float))

    # gamelog = gamelog.fillna("")

    # print(gamelog["days_rest"].astype(float))

    if query.minutes_played.min:
        gamelog = gamelog[gamelog["MP"] > query.minutes_played.min]

    if query.minutes_played.max:
        gamelog = gamelog[gamelog["MP"] < query.minutes_played.max]

    if query.inStartingLineup is not None:
        gamelog = gamelog[gamelog["GS"] == query.inStartingLineup]

    # Filter between dates.
    # gamelog = filter_with_bounds(query)
    # over_bound = (
    #     gamelog[gamelog["Date"].dt.year >= query.date.min]
    #     if query.date.min
    #     else pd.DataFrame()
    # )
    # under_bound = (
    #     gamelog[gamelog["Date"].dt.year <= query.date.max]
    #     if query.date.max
    #     else pd.DataFrame()
    # )

    # print(over_bound)
    # gamelog = pd.concat([over_bound, under_bound])

    # Filter by W/L margin
    gamelog = filter_with_bounds(
        gamelog, "margin", (query.margin.min, query.margin.max)
    )

    gamelog = filter_with_bounds(
        gamelog, "days_rest", (query.daysRest.min, query.daysRest.max)
    )

    if query.gameLocation == "home":
        gamelog = gamelog[gamelog["home"] == True]
    elif query.gameLocation == "away":
        gamelog = gamelog[gamelog["home"] == False]

    # if query.margin.over:
    #     gamelog = gamelog[gamelog["margin"] >= query.margin.over]

    # if query.margin.under:
    #     gamelog = gamelog[gamelog["margin"] <= query.margin.under]

    if query.withoutTeammates:
        for teammate in query.withoutTeammates:

            teammate_id = BasicInfo.get_player_id_from_name(player_name=teammate)

            # TODO: move this inside of the get_player_id function
            if not teammate_id:
                raise DBNotFoundException(
                    f"No player id found for teammate: {teammate}."
                )

            teammate_gamelogs = PlayerBoxScores.filter_records(
                query={"player_id": teammate_id}, as_df=True
            )

            if teammate_gamelogs.empty:
                logger.warning(f"No gamelogs for teammate {teammate}.")
                continue

            overlapping_games = gamelog.merge(
                teammate_gamelogs, on=["Date", "Tm"], suffixes=("", "_x")
            )

            if overlapping_games.empty:
                logger.warning(f"No overlapping games with teammate {teammate}.")
                continue

            games_without_teammate = overlapping_games[
                overlapping_games["G_x"].isnull()
            ]

            gamelog = games_without_teammate[gamelog.columns]

    if query.withTeammates:
        for teammate_id in query.withTeammates:

            teammate_gamelogs = PlayerBoxScores.filter_records(
                query={"player_id": teammate_id}, as_df=True
            )

            if teammate_gamelogs.empty:
                logger.warning(f"No gamelogs for teammate {teammate_id}.")
                continue

            overlapping_games = gamelog.merge(
                teammate_gamelogs, on=["Date", "Tm"], suffixes=("", "_x")
            )

            if overlapping_games.empty:
                logger.warning(f"No overlapping games with teammate {teammate_id}.")
                continue

            games_with_teammate = overlapping_games[
                overlapping_games["G_x"].isnull() == False
            ]

            gamelog = games_with_teammate[gamelog.columns]

    gamelog = gamelog.sort_values("Date")

    if query.limit:
        gamelog = gamelog.tail(query.limit)

    gamelog = gamelog.fillna("")

    return gamelog


def get_matchup_gamelog_by_player_id(*, player_id: str) -> pd.DataFrame:
    matchup_if_home_player: MatchupReadSerializer = Matchups.get_record(query={"home_player_id": player_id})  # type: ignore
    matchup_if_away_player = Matchups.get_record(query={"away_player_id": player_id})

    if matchup_if_home_player:
        matchup = matchup_if_home_player
        home_player = True
    elif matchup_if_away_player:
        matchup = matchup_if_away_player
        home_player = False
    else:
        return pd.DataFrame()

    home_player_df: pd.DataFrame = PlayerBoxScores.filter_records(
        query={"player_id": matchup.home_player.id}, as_df=True  # type: ignore
    )
    away_player_df: pd.DataFrame = PlayerBoxScores.filter_records(
        query={"player_id": matchup.away_player.id}, as_df=True  # type: ignore
    )

    if home_player_df.empty or away_player_df.empty:
        return pd.DataFrame()

    # Merge the datasets on games they played against each other and drop inactive games
    matchup_gamelog = pd.merge(
        home_player_df,
        away_player_df,
        left_on=["Date", "Tm"],
        right_on=["Date", "Opp"],
    ).dropna()

    # Get the original column names of the datasets that were not duplicated
    column_headers = home_player_df.columns.to_list()
    column_headers.pop(column_headers.index("Date"))

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

    return matchup_data
