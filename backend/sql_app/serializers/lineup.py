from pydantic import BaseModel as BaseSerializer
from pydantic import UUID4
from typing import Optional

from .player import PlayerSerializer
from .game import ReadGameSerializer
from .team import ReadTeamSerializer


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
    # Bench: Optional[list]


class LineupReadSerializer(BaseSerializer):
    game: ReadGameSerializer
    team: ReadTeamSerializer
    status: str
    PG: PlayerSerializer
    SG: PlayerSerializer
    SF: PlayerSerializer
    PF: PlayerSerializer
    C: PlayerSerializer
    injuries: list[dict[str, str]] = []
