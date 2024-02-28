from pydantic import BaseModel as BaseSerializer
from pydantic import UUID4
from typing import Optional
from sql_app.serializers.player_info import PlayerSerializer


class LineupSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    team: str
    status: str
    PG_id: str
    SG_id: str
    SF_id: str
    PF_id: str
    C_id: str
    injuries: list[dict[str, str]] = []
    # Bench: Optional[list]


class LineupReadSerializer(BaseSerializer):
    game_id: UUID4
    team: str
    status: str
    PG: PlayerSerializer
    SG: PlayerSerializer
    SF: PlayerSerializer
    PF: PlayerSerializer
    C: PlayerSerializer
    injuries: list[dict[str, str]] = []
