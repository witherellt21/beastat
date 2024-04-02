from typing import Literal, Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .player import PlayerSerializer


class PlayerPropSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    status: Literal[0, 1]
    stat: str
    line: float
    over: int
    over_implied: float
    under: int
    under_implied: float
    player_id: str


class ReadPlayerPropSerializer(BaseSerializer):
    game_id: UUID4
    status: Literal[0, 1]
    line: float | None = None
    stat: str
    over: int
    under: int
    over_implied: float
    under_implied: float
    player: Optional[PlayerSerializer]


class PlayerPropTableEntrySerializer(PlayerPropSerializer):
    game_id: str
    status: int
