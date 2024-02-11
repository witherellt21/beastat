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


class MatchupSerializer(BaseSerializer):
    home_player: str
    away_player: str
    home_player_id: Optional[str]
    away_player_id: Optional[str]
