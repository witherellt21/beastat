from fastapi import HTTPException, status
from typing import List, Optional

from fastapi import APIRouter

from helpers.db_helpers import get_matchup_gamelog
from sql_app.register.matchup import Matchups
from sql_app.serializers.matchup import MatchupSerializer
from sql_app.serializers.matchup import MatchupReadSerializer
from sql_app.serializers.gamelog import GamelogSerializer
from sql_app.serializers.lineup import LineupSerializer
from sql_app.register.lineup import Lineups
from sql_app.register.defense_ranking import DefenseRankings
from sql_app.serializers.defense_ranking import DefenseRankingSerializer

from typing import List
import logging
import pandas as pd


logger = logging.getLogger("main")

router = APIRouter()


def get_defensive_rank_summary_by_position(*, team: str, position: str) -> pd.DataFrame:
    """
    Get the best and worst stat matchups against the position for the given opponent.
    """
    # Get the teams stat rankings against all positions
    defense_rankings = DefenseRankings.filter_records(
        query={"team_abr": team}, as_df=True
    )

    if defense_rankings.empty:
        return pd.DataFrame()

    # Get a series containing the stat ranks against the given position

    stat_ranks = defense_rankings[["stat", position]]
    stat_ranks = stat_ranks.rename(columns={position: "value"})

    overall_rank = stat_ranks[stat_ranks["stat"] == "OVR"]
    stat_ranks = stat_ranks[stat_ranks["stat"] != "OVR"]

    sorted_stats = stat_ranks.sort_values("value")
    strongest_stats = sorted_stats.head(2)
    weakest_stats = sorted_stats.tail(2)

    # Create summary of best and worst stat matchups, plus the overall rank against the positions
    stat_summary = pd.concat([strongest_stats, weakest_stats, overall_rank])

    return stat_summary


############################
# ListMatchups
############################


@router.get("/")
async def list_matchups():
    matchups: List[MatchupReadSerializer] = Matchups.get_all_records()  # type: ignore

    result = []
    for matchup in matchups:
        lineup: LineupSerializer = Lineups.get_record(query={"game_id": matchup.game_id, "home": True})  # type: ignore

        home_defense_rank_summary = get_defensive_rank_summary_by_position(
            team=lineup.team, position=matchup.position
        )

        away_defense_rank_summary = get_defensive_rank_summary_by_position(
            team=lineup.opp, position=matchup.position
        )

        matchup_data = matchup.model_dump()
        matchup_data["home_def_rank_summary"] = (
            home_defense_rank_summary.to_dict(orient="records")
            if not home_defense_rank_summary.empty
            else {}
        )
        matchup_data["away_def_rank_summary"] = (
            away_defense_rank_summary.to_dict(orient="records")
            if not away_defense_rank_summary.empty
            else {}
        )

        matchup_data["home_defense_ranking_overall"] = int(
            home_defense_rank_summary.set_index("stat").loc["OVR"]["value"]
        )
        matchup_data["away_defense_ranking_overall"] = int(
            away_defense_rank_summary.set_index("stat").loc["OVR"]["value"]
        )

        result.append(matchup_data)

    return result


@router.get("/byGame")
async def list_matchups_by_game():
    lineups: List[LineupSerializer] = Lineups.filter_records(query={"home": True})  # type: ignore

    result = []
    for lineup in lineups:
        matchups: List[MatchupReadSerializer] = Matchups.filter_records(query={"game_id": lineup.game_id})  # type: ignore

        matchup_result = []
        for matchup in matchups:

            home_defense_rank_summary = get_defensive_rank_summary_by_position(
                team=lineup.team, position=matchup.position
            )

            away_defense_rank_summary = get_defensive_rank_summary_by_position(
                team=lineup.opp, position=matchup.position
            )

            matchup_data = matchup.model_dump()

            if not home_defense_rank_summary.empty:
                matchup_data["home_def_rank_summary"] = (
                    home_defense_rank_summary.to_dict(orient="records")
                    if not home_defense_rank_summary.empty
                    else {}
                )
                matchup_data["home_defense_ranking_overall"] = int(
                    home_defense_rank_summary.set_index("stat").loc["OVR"]["value"]
                )

            if not away_defense_rank_summary.empty:
                matchup_data["away_def_rank_summary"] = (
                    away_defense_rank_summary.to_dict(orient="records")
                    if not away_defense_rank_summary.empty
                    else {}
                )

                matchup_data["away_defense_ranking_overall"] = int(
                    away_defense_rank_summary.set_index("stat").loc["OVR"]["value"]
                )

            matchup_result.append(matchup_data)

        game_data = {
            "home": lineup.team,
            "away": lineup.opp,
            "matchups": matchup_result,
        }
        result.append(game_data)

    return result


############################
# RetrieveMatchup
############################


@router.get("/{id}")
async def retrieve_matchup(id: str):
    matchup: MatchupReadSerializer = Matchups.get_record(query={"id": id})  # type: ignore

    # lineup: LineupSerialzer = Lineups.get_record(query={"game_id": matchup.game_id})  # type: ignore
    # home_defense_ranking: DefenseRankingSerializer = DefenseRankings.get_record(query={"team_abr": lineup.team, "stat": "OVR"})  # type: ignore
    # away_defense_ranking: DefenseRankingSerializer = DefenseRankings.get_record(query={"team_abr": lineup.opp, "stat": "OVR"})  # type: ignore

    # matchup_data = matchup.model_dump()
    # matchup_data["home_defense_ranking"] = getattr(
    #     home_defense_ranking, matchup.position, None
    # )
    # matchup_data["away_defense_ranking"] = getattr(
    #     away_defense_ranking, matchup.position, None
    # )

    if matchup:
        return matchup
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Matchup not found with id: {id}.",
        )


############################
# RetrieveMatchupStats
############################

import traceback


@router.get("/{id}/stats/{home_away}", response_model=List[GamelogSerializer])
async def retrieve_matchup_stats(id: str, home_away: str):
    try:
        if home_away == "home":
            matchup = get_matchup_gamelog(id=id)
        else:
            matchup = get_matchup_gamelog(id=id, home_player=False)

        logger.debug(matchup)

        return matchup
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {e}",
        )
