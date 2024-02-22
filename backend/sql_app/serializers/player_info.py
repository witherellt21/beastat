from pydantic import BaseModel as BaseSerializer
import datetime


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


class PlayerInfoReadSerializer(BaseSerializer):
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
