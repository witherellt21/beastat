from pydantic import BaseModel as BaseSerializer
import datetime


class PlayerPropSerializer(BaseSerializer):
    player_id: str
    player_name: str
    stat: str
    line: float
    odds_over: int
    implied_odds_over: float
    odds_under: int
    implied_odds_under: float
    timestamp: datetime.datetime
