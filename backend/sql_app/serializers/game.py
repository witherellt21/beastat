from pydantic import BaseModel as BaseSerializer
from pydantic import StringConstraints
from pydantic import UUID4
from datetime import datetime
from typing import Optional, Annotated
import uuid


class GameSerializer(BaseSerializer):
    id: UUID4
    date_time: datetime
    home: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    away: Annotated[str, StringConstraints(min_length=3, max_length=3)]  # type: ignore
    line: Optional[str] = None
    spread: Optional[str] = None
    over_under: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    winner: Optional[Annotated[str, StringConstraints(min_length=3, max_length=3)]] = None  # type: ignore
    victory_margin: Optional[int] = None
    timestamp: datetime
