from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .game import GameReadSerializer
from .player import PlayerSerializer


class MatchupSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    position: str
    home_player_id: str
    away_player_id: str


class MatchupReadSerializer(BaseSerializer):
    id: str
    game: GameReadSerializer
    position: str
    home_player: PlayerSerializer
    away_player: PlayerSerializer


class MatchupUpdateSerializer(BaseSerializer):
    game: GameReadSerializer
    position: str
    home_player: PlayerSerializer
    away_player: PlayerSerializer
