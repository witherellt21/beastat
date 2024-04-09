import datetime
from typing import Literal, Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .game import GameSerializer
from .team import TeamReadSerializer


class PlayerSerializer(BaseSerializer):
    id: str
    team_id: Optional[UUID4]
    name: str
    nicknames: list[str] = []
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date
    timestamp: datetime.datetime  # timestamp in epoch


class PlayerReadSerializer(PlayerSerializer):
    id: str

    _team_id: Optional[UUID4]
    team: Optional[TeamReadSerializer]


class PlayerUpdateSerializer(PlayerSerializer):
    pass


####################
# Player Props
####################


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
