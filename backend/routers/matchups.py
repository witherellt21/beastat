from fastapi import HTTPException, status
from typing import List

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


logger = logging.getLogger("main")

router = APIRouter()


############################
# ListMatchups
############################


@router.get("/")
async def list_matchups():
    matchups: List[MatchupReadSerializer] = Matchups.get_all_records()  # type: ignore

    result = []
    for matchup in matchups:
        lineup: LineupSerializer = Lineups.get_record(query={"game_id": matchup.game_id, "home": True})  # type: ignore
        home_defense_ranking: DefenseRankingSerializer = DefenseRankings.get_record(query={"team_abr": lineup.team, "stat": "OVR"})  # type: ignore
        away_defense_ranking: DefenseRankingSerializer = DefenseRankings.get_record(query={"team_abr": lineup.opp, "stat": "OVR"})  # type: ignore

        matchup_data = matchup.model_dump()
        matchup_data["home_defense_ranking"] = getattr(
            home_defense_ranking, matchup.position, None
        )
        matchup_data["away_defense_ranking"] = getattr(
            away_defense_ranking, matchup.position, None
        )
        result.append(matchup_data)

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
