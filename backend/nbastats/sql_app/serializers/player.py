import datetime
from typing import Optional

from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .team import ReadTeamSerializer


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


class PlayerTableEntrySerializer(BaseSerializer):
    id: str
    team_id: Optional[str]
    name: str
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date


class ReadPlayerSerializer(BaseSerializer):
    id: str
    team: Optional[ReadTeamSerializer]
    name: str
    nicknames: list[str] = []
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date
    timestamp: datetime.datetime  # timestamp in epoch


class UpdatePlayerSerializer(BaseSerializer):
    id: str
    team: Optional[ReadTeamSerializer]
    name: str
    nicknames: list[str] = []
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date
    timestamp: datetime.datetime  # timestamp in epoch
