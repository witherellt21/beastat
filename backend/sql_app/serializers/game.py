import uuid
from datetime import datetime
from typing import Annotated, Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer
from pydantic import StringConstraints

from .team import ReadTeamSerializer


class GameSerializer(BaseSerializer):
    id: UUID4
    date_time: datetime
    # home: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    # away: Annotated[str, StringConstraints(min_length=3, max_length=3)]  # type: ignore
    home_id: UUID4
    away_id: UUID4
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[Annotated[str, StringConstraints(min_length=3, max_length=3)]] = None  # type: ignore
    victory_margin: Optional[int] = None
    timestamp: datetime


class ReadGameSerializer(BaseSerializer):
    id: UUID4
    date_time: datetime
    home: ReadTeamSerializer
    away: ReadTeamSerializer
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[Annotated[str, StringConstraints(min_length=3, max_length=3)]] = None  # type: ignore
    victory_margin: Optional[int] = None
    timestamp: datetime


class GameLineSerializer(BaseSerializer):
    game_id: UUID4
    favored_team_id: UUID4
    line: float
    spread: float
    over_under: float


class ReadGameLineSerializer(BaseSerializer):
    game: ReadGameSerializer
    favored_team: ReadTeamSerializer
    line: float
    spread: float
    over_under: float
