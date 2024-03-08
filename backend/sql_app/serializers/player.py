from pydantic import BaseModel as BaseSerializer
import datetime


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
