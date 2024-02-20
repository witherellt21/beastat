from fastapi import Response, Request
from fastapi import Depends, FastAPI, HTTPException, status
from typing import List

from fastapi import APIRouter

import pandas as pd

from helpers.db_helpers import get_matchup_gamelog_by_player_id
from pydantic import TypeAdapter
from sql_app.register.gamelog import Gamelogs
from sql_app.serializers.gamelog import GamelogSerializer

import datetime

from typing import List
import logging

logger = logging.getLogger("main")

router = APIRouter()

############################
# GetGamelogByPlayerID
############################


@router.get("/{id}")
async def get_gamelog_by_player_id(
    id: str, query: str, startyear: str = None, matchups_only: bool = False
):
    try:
        if matchups_only:
            gamelog: pd.DataFrame = get_matchup_gamelog_by_player_id(player_id=id)
            print(gamelog)
        else:
            gamelog: pd.DataFrame = Gamelogs.filter_records(
                query={"player_id": id}, as_df=True
            )

        if not gamelog.empty:
            queried: pd.DataFrame = gamelog.query(query)
            queried = queried.fillna("")

            if startyear:
                try:
                    # year = datetime.datetime(int(startyear))
                    queried = queried[queried["Date"].dt.year >= int(startyear)]
                    print(queried)
                except Exception as e:
                    print(e)

            as_dict = queried.to_dict(orient="records")
            # list_type: TypeAdapter = TypeAdapter(List[GamelogSerializer])
            # validated_data = list_type.validate_python(
            #     queried.to_dict(orient="records")
            # )
            # print(validated_data)
            # return validated_data
            return as_dict
        else:
            return []

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error retrieving the player's gamelogs. {e}",
        )
