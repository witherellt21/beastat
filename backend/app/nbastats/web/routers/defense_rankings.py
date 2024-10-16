import logging

from fastapi import APIRouter
from nbastats.db.register import DefenseRankings, Games
from nbastats.db.register.serializers import GameReadSerializer

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
    game: GameReadSerializer = Games.get_record(query={"id": game_id})  # type: ignore

    if not game:
        return {}

    # TODO: Temporary solution to team_abr problems
    team_abr = {"UTA": "UTH", "PHX": "PHO"}

    home_stat_rankings = DefenseRankings.filter_records(
        query={"team_abr": team_abr.get(game.home.name, game.home.name)}, as_df=True
    )
    away_stat_rankings = DefenseRankings.filter_records(
        query={"team_abr": team_abr.get(game.away.name, game.away.name)}, as_df=True
    )

    home_stat_rankings = home_stat_rankings[["stat", position]]
    away_stat_rankings = away_stat_rankings[["stat", position]]

    home_stat_rankings = home_stat_rankings.set_index("stat").T
    away_stat_rankings = away_stat_rankings.set_index("stat").T

    return {
        "home": home_stat_rankings.to_dict(orient="records")[0],
        "away": away_stat_rankings.to_dict(orient="records")[0],
    }
