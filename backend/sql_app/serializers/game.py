from pydantic import BaseModel as BaseSerializer
from pydantic import constr
from pydantic import UUID4
from datetime import datetime
from typing import Optional
import uuid


class GameSerializer(BaseSerializer):
    id: UUID4
    date_time: datetime
    home: constr(max_length=3)  # type: ignore
    away: constr(max_length=3)  # type: ignore
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[constr(max_length=3)] = None  # type: ignore
    victory_margin: Optional[int] = None
    timestamp: datetime
