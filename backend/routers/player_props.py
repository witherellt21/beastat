from fastapi import APIRouter

from sql_app.serializers.player_prop import PlayerPropSerializer
from sql_app.register.player_prop import PlayerProps

import logging

logger = logging.getLogger("main")

router = APIRouter()

############################
# GetPropsByPlayerID
############################


@router.get("/{player_id}", response_model=PlayerPropSerializer)
async def get_props_by_player_id(player_id: str):
    player_props = PlayerProps.filter_records(
        query={"player_id": player_id}, as_df=True
    )

    return None


# if __name__ == "__main__":
