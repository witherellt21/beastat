from typing import Optional
from pydantic import BaseModel as BaseSerializer
from pydantic import UUID4
from sql_app.serializers.player import PlayerSerializer


class CareerStatsSerializer(BaseSerializer):
    id: UUID4
    player_id: str
    Season: str
    Age: Optional[float]
    Tm: str
    Lg: str
    Pos: str
    G: int
    GS: int
    MP: float
    FG: Optional[float]
    FGA: Optional[float]
    FG_perc: Optional[float]
    THP: Optional[float]
    THPA: Optional[float]
    THP_perc: Optional[float]
    TWP: Optional[float]
    TWPA: Optional[float]
    TWP_perc: Optional[float]
    eFG_perc: Optional[float]
    FT: Optional[float]
    FTA: Optional[float]
    FT_perc: Optional[float]
    ORB: Optional[float]
    DRB: Optional[float]
    TRB: Optional[float]
    AST: Optional[float]
    STL: Optional[float]
    BLK: Optional[float]
    TOV: Optional[float]
    PF: Optional[float]
    PTS: Optional[float]
    Awards: Optional[str]
    PA: Optional[float]
    PR: Optional[float]
    RA: Optional[float]
    PRA: Optional[float]


class CareerStatsReadSerializer(BaseSerializer):
    id: UUID4
    player: PlayerSerializer
    Season: str
    Age: Optional[float]
    Tm: str
    Lg: str
    Pos: str
    G: int
    GS: int
    MP: float
    FG: Optional[float]
    FGA: Optional[float]
    FG_perc: Optional[float]
    THP: Optional[float]
    THPA: Optional[float]
    THP_perc: Optional[float]
    TWP: Optional[float]
    TWPA: Optional[float]
    TWP_perc: Optional[float]
    eFG_perc: Optional[float]
    FT: Optional[float]
    FTA: Optional[float]
    FT_perc: Optional[float]
    ORB: Optional[float]
    DRB: Optional[float]
    TRB: Optional[float]
    AST: Optional[float]
    STL: Optional[float]
    BLK: Optional[float]
    TOV: Optional[float]
    PF: Optional[float]
    PTS: Optional[float]
    Awards: Optional[str]
    PA: Optional[float]
    PR: Optional[float]
    RA: Optional[float]
    PRA: Optional[float]
