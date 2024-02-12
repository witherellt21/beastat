from pydantic import BaseModel as BaseSerializer
from typing import Optional


class MatchupSerializer(BaseSerializer):
    game_id: int
    position: str
    home_player: str
    away_player: str
    home_player_id: Optional[str]
    away_player_id: Optional[str]


class MatchupReadSerializer(BaseSerializer):
    id: int
    game_id: int
    position: str
    home_player: str
    away_player: str
    home_player_id: Optional[str]
    away_player_id: Optional[str]
