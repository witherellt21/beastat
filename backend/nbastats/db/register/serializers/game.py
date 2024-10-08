from datetime import datetime
from typing import Annotated, Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer
from pydantic import StringConstraints

from .team import TeamReadSerializer


class BaseGameSerializer(BaseSerializer):
    # id: UUID4
    date_time: datetime
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[Annotated[str, StringConstraints(min_length=3, max_length=3)]] = None  # type: ignore
    victory_margin: Optional[int] = None
    timestamp: datetime


class GameSerializer(BaseGameSerializer):
    id: UUID4
    # home: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    # away: Annotated[str, StringConstraints(min_length=3, max_length=3)]  # type: ignore
    home_id: UUID4
    away_id: UUID4


class GameReadSerializer(BaseGameSerializer):
    id: UUID4
    # new fields
    home: TeamReadSerializer
    away: TeamReadSerializer


class GameLineSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    favored_team_id: UUID4
    line: float
    spread: float
    over_under: float


class GameLineReadSerializer(GameLineSerializer):

    id: str

    _game_id: UUID4
    _favored_team_id: UUID4
    game: GameReadSerializer
    favored_team: TeamReadSerializer
