from pydantic import BaseModel as BaseSerializer


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
