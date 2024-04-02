from fastapi import APIRouter, HTTPException, status
from nbastats.sql_app.models import Player, PropLine
from playhouse.shortcuts import model_to_dict

router = APIRouter()


@router.get("/{player_id}")
def get_player(player_id: str):
    # player = Players.get_with_prop_lines(query={"id": player_id})
    # return player
    player = (
        Player.select(Player, PropLine).join(PropLine).where(Player.id == player_id)
    )

    for p in player:
        as_dict = model_to_dict(p)

    return as_dict


# @router.get("/{player_id}/team")
# def get_player_team(player_id: str):
#     currentStats: CareerStatsReadSerializer = CareerStatss.get_record(
#         query={"player_id": player_id, "Season": 2024}
#     )  # type: ignore

#     current_team = currentStats.Tm
