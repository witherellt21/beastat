from pydantic import BaseModel as BaseSerializer
from pydantic import UUID4
from typing import Optional

from sql_app.serializers.player import PlayerSerializer
from sql_app.serializers.game import ReadGameSerializer


class MatchupSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    position: str
    home_player_id: str
    away_player_id: str


class MatchupReadSerializer(BaseSerializer):
    id: UUID4
    game: ReadGameSerializer
    position: str
    home_player: PlayerSerializer
    away_player: PlayerSerializer


class MatchupUpdateSerializer(BaseSerializer):
    game: ReadGameSerializer
    position: str
    home_player: PlayerSerializer
    away_player: PlayerSerializer
