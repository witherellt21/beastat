from typing import Literal, Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .game import GameSerializer
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


class PlayerPropReadSerializer(PlayerPropSerializer):
    id: str

    _game_id: UUID4
    game: GameSerializer

    _player_id: str
    player: Optional[PlayerSerializer]
