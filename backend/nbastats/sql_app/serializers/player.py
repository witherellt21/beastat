import datetime
from typing import Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

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
