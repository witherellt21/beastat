import pandas as pd
from fastapi import APIRouter

from sql_app.serializers.player_prop import PlayerPropSerializer
from sql_app.serializers.player_prop import ReadPlayerPropSerializer
from sql_app.serializers.player_prop import ReadPropLineSerializer
from sql_app.register.player_prop import PlayerProps
from sql_app.register.player_prop import PropLines
from typing import List

import logging

logger = logging.getLogger("main")


router = APIRouter()

############################
# GetPropsByPlayerID
############################


@router.get("/{player_id}")
async def get_props_by_player_id(player_id: str):
    # lines = PropLines.filter_records(query="player_id")
    player: PlayerPropSerializer = PlayerProps.get_record(
        query={"player_id": player_id}
    )

    if not player:
        print(f"No prop lines for player: {player_id}")
        return []

    # logger.debug(player)
    lines: list[ReadPropLineSerializer] = PropLines.filter_records(
        query={"player_id": player.id}
    )

    # player_lines = {line.stat: }
    new_lines = {}
    for line in lines:
        new_lines[line.stat] = {
            "line": line.line,
            "over": line.over,
            "under": line.under,
            "over_implied": line.over_implied,
            "under_implied": line.under_implied,
        }

    return [new_lines]

    # player_props: pd.DataFrame = PlayerProps.filter_records(
    #     query={"player_id": player_id}, as_df=True
    # )

    # if player_props.empty:
    #     return ReadPlayerPropSerializer(player_name=player_id)

    # # grouped_by_stat = player_props.groupby("stat")
    # stat_types = player_props["stat"].values

    # # line_slice = player_props[
    # #     "stat",
    # #     "line",
    # #     "odds_over",
    # #     "odds_under",
    # #     "implied_odds_over",
    # #     "implied_odds_under",
    # # ]
    # ast_line: pd.DataFrame = player_props[player_props["stat"] == "assists"]

    # if not ast_line.empty:
    #     ast_line: object = ast_line.iloc[0]

    #     validated_data: PlayerPropSerializer = PlayerPropSerializer(**ast_line)

    #     payload = {
    #         "player_name": validated_data.player_name,
    #         "AST": {
    #             "line": validated_data.line,
    #             "over": {
    #                 "odds": validated_data.odds_over,
    #                 "implied_odds": validated_data.implied_odds_over,
    #             },
    #             "under": {
    #                 "odds": validated_data.odds_under,
    #                 "implied_odds": validated_data.implied_odds_under,
    #             },
    #         },
    #     }

    #     response_data = ReadPlayerPropSerializer(**payload)

    #     return [response_data]

    # return ReadPlayerPropSerializer(player_name=player_id)

    # payload = {
    #     'player_name': player_props.loc[]
    # }


# if __name__ == "__main__":
