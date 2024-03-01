from pydantic import BaseModel as BaseSerializer
import datetime
from typing import Optional


class PlayerInfoSerializer(BaseSerializer):
    player_id: str
    name: str
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date
    timestamp: datetime.datetime  # timestamp in epoch


class PlayerSerializer(BaseSerializer):
    id: str
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
    name: str
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date


class PlayerInfoReadSerializer(BaseSerializer):
    player_id: str
    name: str
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date


class PlayerInfoTableEntrySerializer(BaseSerializer):
    player_id: str
    name: str
    active_from: int
    active_to: int
    position: str
    height: int
    weight: int
    birth_date: datetime.date


class CollegeSerializer(BaseSerializer):
    name: str
    player_info: str
