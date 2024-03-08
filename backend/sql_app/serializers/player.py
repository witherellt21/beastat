from pydantic import BaseModel as BaseSerializer
from pydantic import UUID4
import datetime

from . import TeamSerializer


class PlayerSerializer(BaseSerializer):
    id: str
    team_id: UUID4
    name: str
    nicknames: list[str] = []
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date
    timestamp: datetime.datetime  # timestamp in epoch


class PlayerTableEntrySerializer(BaseSerializer):
    id: str
    team: TeamSerializer
    name: str
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date
