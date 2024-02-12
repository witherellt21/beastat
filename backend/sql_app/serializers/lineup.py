from pydantic import BaseModel as BaseSerializer
from typing import Optional


class LineupSerialzer(BaseSerializer):
    game_id: int
    team: str
    opp: str
    home: bool
    confirmed: bool
    PG: str
    SG: str
    SF: str
    PF: str
    C: str
    # Bench: Optional[list]
