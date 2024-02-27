import pandas as pd
from fastapi import APIRouter

from sql_app.register.defense_ranking import DefenseRankings
from sql_app.register.player_prop import PlayerProps
from sql_app.register.player_prop import PropLines
from sql_app.register.gamelog import Gamelogs
from sql_app.register.lineup import Lineups
from sql_app.register.game import Games
from sql_app.serializers.game import GameSerializer
from sql_app.serializers.lineup import LineupSerializer
from typing import List

import logging

logger = logging.getLogger("main")


router = APIRouter()

############################
# GetPropsByPlayerID
############################


@router.get("/{team_abr}/{position}")
async def get_defense_rankings_by_team_and_position(team_abr: str, position: str):
    stat_rankings = DefenseRankings.filter_records(
        query={"team_abr": team_abr}, as_df=True
    )
    stat_rankings = stat_rankings[["stat", position]]
    stat_rankings = stat_rankings.set_index("stat").T

    return stat_rankings.to_dict(orient="records")


@router.get("/game/{game_id}/{position}")
async def get_defense_rankings_for_game(game_id: str, position: str):
    game: GameSerializer = Games.get_record(query={"id": game_id})  # type: ignore

    if not game:
        return {}

    home_stat_rankings = DefenseRankings.filter_records(
        query={"team_abr": game.home}, as_df=True
    )
    away_stat_rankings = DefenseRankings.filter_records(
        query={"team_abr": game.away}, as_df=True
    )

    home_stat_rankings = home_stat_rankings[["stat", position]]
    away_stat_rankings = away_stat_rankings[["stat", position]]

    home_stat_rankings = home_stat_rankings.set_index("stat").T
    away_stat_rankings = away_stat_rankings.set_index("stat").T

    return {
        "home": home_stat_rankings.to_dict(orient="records")[0],
        "away": away_stat_rankings.to_dict(orient="records")[0],
    }
