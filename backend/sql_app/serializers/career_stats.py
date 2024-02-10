from typing import Optional
from pydantic import BaseModel as BaseSerializer

class CareerStatsSerializer(BaseSerializer):
    player_id : str
    Season : str
    Age : Optional[float]
    Tm : str
    Lg : str
    Pos : str
    G : int
    GS : int
    MP : float
    FG : float
    FGA : float
    FG_perc : float
    THP : float
    THPA : float
    THP_perc : Optional[float]
    TWP : float
    TWPA : float
    TWP_perc : float
    eFG_perc : float
    FT : float
    FTA : float
    FT_perc : float
    ORB : float
    DRB : float
    TRB : float
    AST : float
    STL : float
    BLK : float
    TOV : float
    PF : float
    PTS : float
    Awards : str
    PA : float
    PR : float
    RA : float
    PRA : float