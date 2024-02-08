import datetime
from pydantic import BaseModel as BaseSerializer
from typing import Optional

class GamelogSerializer(BaseSerializer):
    player_id: str
    G: Optional[float]
    Date: datetime.datetime
    Age: str
    Tm: str
    Opp: str
    streak: str
    GS: Optional[float]
    MP: Optional[float]
    FG: Optional[float]
    FGA: Optional[float]
    FG_perc: Optional[float]
    THP: Optional[float]
    THPA: Optional[float]
    THP_perc: Optional[float]
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
    GmSc: Optional[float]
    PA: Optional[float]
    PR: Optional[float]
    RA: Optional[float]
    PRA: Optional[float]