from pydantic import UUID4
from pydantic import BaseModel as BaseSerializer

from .game import GameReadSerializer
from .player import PlayerInsertSerializer
from .team import TeamReadSerializer


class LineupSerializer(BaseSerializer):
    id: UUID4
    game_id: UUID4
    team_id: UUID4
    status: str
    PG_id: str
    SG_id: str
    SF_id: str
    PF_id: str
    C_id: str
    injuries: list[dict[str, str]] = []


class LineupReadSerializer(LineupSerializer):
    id: str

    _game_id: UUID4
    game: GameReadSerializer

    _team_id: UUID4
    team: TeamReadSerializer

    _PG_id: str
    _SG_id: str
    _SF_id: str
    _PF_id: str
    _C_id: str
    PG: PlayerInsertSerializer
    SG: PlayerInsertSerializer
    SF: PlayerInsertSerializer
    PF: PlayerInsertSerializer
    C: PlayerInsertSerializer
